#!/usr/bin/env python3
"""
Test Runner for Ex4 Uninitialized Variable Analysis Test Suite

Runs both official and unofficial tests against the ANALYZER executable.

Usage:
    python run_tests.py                        # Run all tests
    python run_tests.py --official             # Run only official tests
    python run_tests.py --unofficial           # Run only unofficial tests
    python run_tests.py --category global      # Run specific category
    python run_tests.py --zip 123456789.zip    # Test a submission zip
"""

import os
import sys
import subprocess
import pathlib
import argparse
import zipfile
import tempfile
import shutil
from collections import defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXERCISE_DIR = SCRIPT_DIR / 'ex4'
EXECUTABLE_NAME = "ANALYZER"

# Test directories
OFFICIAL_DIR = SCRIPT_DIR / 'official'
UNOFFICIAL_DIR = SCRIPT_DIR / 'unofficial'

# Categories for unofficial tests
CATEGORIES = ['global', 'local', 'propagation', 'shadow', 'if', 'while',
              'printint', 'expr', 'edge', 'ok']


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message in green"""
    print(f"{Colors.GREEN}{text}{Colors.END}")


def print_error(text):
    """Print error message in red"""
    print(f"{Colors.RED}{text}{Colors.END}")


def print_warning(text):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}{text}{Colors.END}")


def check_analyzer_exists():
    """Check if ANALYZER executable exists"""
    executable_path = EXERCISE_DIR / EXECUTABLE_NAME
    if not executable_path.exists():
        print_error(f"ERROR: ANALYZER executable not found at {executable_path}")
        print_warning("\nPlease build the analyzer first:")
        print_warning("  cd ex4 && make")
        return None
    return executable_path


def extract_submission_zip(zip_path, temp_dir):
    """
    Extract submission zip file to temporary directory

    Returns: (ex4_dir, ids_file) or (None, None) on error
    """
    zip_path = pathlib.Path(zip_path)

    if not zip_path.exists():
        print_error(f"Zip file not found: {zip_path}")
        return None, None

    if not zipfile.is_zipfile(zip_path):
        print_error(f"Not a valid zip file: {zip_path}")
        return None, None

    print_header(f"EXTRACTING SUBMISSION: {zip_path.name}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # List contents
            file_list = zipf.namelist()

            # Verify structure
            if 'ids.txt' not in file_list:
                print_error("ids.txt not found in zip")
                return None, None

            ex4_files = [f for f in file_list if f.startswith('ex4/')]
            if not ex4_files:
                print_error("ex4/ directory not found in zip")
                return None, None

            if 'ex4/Makefile' not in file_list:
                print_error("ex4/Makefile not found in zip")
                return None, None

            print_success(f"✓ Valid submission structure")

            # Extract all files
            zipf.extractall(temp_dir)

            ex4_dir = temp_dir / 'ex4'
            ids_file = temp_dir / 'ids.txt'

            # Show student IDs
            with open(ids_file, 'r') as f:
                ids = f.read().strip().split('\n')
                print(f"\n{Colors.BOLD}Student IDs:{Colors.END}")
                for student_id in ids:
                    if student_id.strip():
                        print(f"  - {student_id.strip()}")

            print_success(f"✓ Extracted {len(ex4_files)} files from ex4/")

            return ex4_dir, ids_file

    except Exception as e:
        print_error(f"Failed to extract zip: {e}")
        return None, None


def build_analyzer_from_submission(ex4_dir):
    """
    Build ANALYZER from extracted submission

    Returns: Path to ANALYZER executable or None on failure
    """
    print_header("BUILDING ANALYZER")

    makefile = ex4_dir / 'Makefile'
    if not makefile.exists():
        print_error("Makefile not found in ex4 directory")
        return None

    print(f"Running 'make' in {ex4_dir}...")

    try:
        process = subprocess.run(
            ["make"],
            cwd=str(ex4_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=60
        )

        if process.returncode != 0:
            print_error("Build failed!")
            print("\nSTDOUT:")
            print(process.stdout)
            print("\nSTDERR:")
            print(process.stderr)
            return None

        print_success("✓ Build successful")

        # Check if ANALYZER was created
        analyzer_path = ex4_dir / EXECUTABLE_NAME
        if not analyzer_path.exists():
            print_error(f"ANALYZER executable not created at {analyzer_path}")
            return None

        print_success(f"✓ ANALYZER created at {analyzer_path}")
        return analyzer_path

    except subprocess.TimeoutExpired:
        print_error("Build timed out (>60s)")
        return None
    except Exception as e:
        print_error(f"Build failed: {e}")
        return None


def run_single_test(test_file, expected_output_file, executable_path, verbose=False):
    """
    Run a single test and compare output

    Returns: (passed, error_message)
    """
    # Create temporary output file
    output_file = pathlib.Path(f"/tmp/test_output_{test_file.stem}.txt")

    # ANALYZER requires an 'output' directory relative to cwd for debug files
    analyzer_dir = executable_path.resolve().parent
    output_dir = analyzer_dir / 'output'
    output_dir.mkdir(exist_ok=True)

    try:
        # Run the analyzer from its directory
        process = subprocess.run(
            ["java", "-jar", str(executable_path.resolve()), str(test_file.resolve()), str(output_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            universal_newlines=True,
            cwd=str(analyzer_dir)
        )

        # Check subprocess return code
        if process.returncode != 0:
            error_msg = f"ANALYZER failed with exit code {process.returncode}"
            if process.stderr:
                error_msg += f"\nSTDERR: {process.stderr.strip()}"
            if process.stdout:
                error_msg += f"\nSTDOUT: {process.stdout.strip()}"
            return False, error_msg

        # Check if output file was created
        if not output_file.exists():
            return False, "Output file not created"

        # Read actual and expected output
        with open(output_file, 'r') as f:
            actual_output = f.read()

        with open(expected_output_file, 'r') as f:
            expected_output = f.read()

        # Compare outputs
        if actual_output == expected_output:
            if verbose:
                print(f"  Expected: {repr(expected_output)}")
                print(f"  Actual:   {repr(actual_output)}")
            return True, None
        else:
            error_msg = f"Output mismatch\n  Expected: {repr(expected_output)}\n  Actual:   {repr(actual_output)}"
            return False, error_msg

    except subprocess.TimeoutExpired:
        return False, "Timeout (>10s)"
    except Exception as e:
        return False, f"Exception: {str(e)}"
    finally:
        # Cleanup
        if output_file.exists():
            output_file.unlink()


def run_official_tests(executable_path, verbose=False):
    """Run all official tests"""
    print_header("OFFICIAL TESTS")

    tests_dir = OFFICIAL_DIR / 'tests'
    expected_dir = OFFICIAL_DIR / 'expected_output'

    if not tests_dir.exists():
        print_warning("No official tests directory found")
        return 0, 0

    test_files = sorted(tests_dir.glob("*.txt"))
    if not test_files:
        print_warning("No official tests found")
        return 0, 0

    passed = 0
    failed = 0
    failed_tests = []

    for test_file in test_files:
        expected_file = expected_dir / f"{test_file.stem}_Expected_Output.txt"

        if not expected_file.exists():
            print_error(f"✗ {test_file.stem}: Expected output file missing")
            failed += 1
            failed_tests.append((test_file.stem, "Expected output file missing"))
            continue

        print(f"Running {test_file.stem}...", end=" ")
        success, error = run_single_test(test_file, expected_file, executable_path, verbose)

        if success:
            print_success("✓ PASS")
            passed += 1
        else:
            print_error(f"✗ FAIL: {error}")
            failed += 1
            failed_tests.append((test_file.stem, error))

    print(f"\n{Colors.BOLD}Official Tests Summary:{Colors.END}")
    print(f"  Total:  {passed + failed}")
    print_success(f"  Passed: {passed}")
    if failed > 0:
        print_error(f"  Failed: {failed}")

    return passed, failed


def run_unofficial_tests(executable_path, category_filter=None, verbose=False):
    """Run all unofficial tests (organized by category)"""
    print_header("UNOFFICIAL TESTS")

    if not UNOFFICIAL_DIR.exists():
        print_warning("No unofficial tests directory found")
        return 0, 0

    categories_to_run = [category_filter] if category_filter else CATEGORIES

    total_passed = 0
    total_failed = 0
    results_by_category = {}

    for category in categories_to_run:
        category_dir = UNOFFICIAL_DIR / category
        tests_dir = category_dir / 'tests'
        expected_dir = category_dir / 'expected_output'

        if not tests_dir.exists():
            print_warning(f"Category '{category}' not found, skipping")
            continue

        test_files = sorted(tests_dir.glob("*.txt"))
        if not test_files:
            continue

        print(f"\n{Colors.BOLD}Category: {category.upper()}{Colors.END}")

        passed = 0
        failed = 0
        failed_tests = []

        for test_file in test_files:
            expected_file = expected_dir / f"{test_file.stem}_Expected_Output.txt"

            if not expected_file.exists():
                print_error(f"  ✗ {test_file.stem}: Expected output file missing")
                failed += 1
                failed_tests.append((test_file.stem, "Expected output file missing"))
                continue

            print(f"  Running {test_file.stem}...", end=" ")
            success, error = run_single_test(test_file, expected_file, executable_path, verbose)

            if success:
                print_success("✓ PASS")
                passed += 1
            else:
                print_error(f"✗ FAIL: {error}")
                failed += 1
                failed_tests.append((test_file.stem, error))

        results_by_category[category] = (passed, failed)
        total_passed += passed
        total_failed += failed

        print(f"  {category}: {passed}/{passed+failed} passed")

    # Summary
    print(f"\n{Colors.BOLD}Unofficial Tests Summary:{Colors.END}")
    for category, (passed, failed) in results_by_category.items():
        total = passed + failed
        status = print_success if failed == 0 else print_error
        print(f"  {category:12} {passed:2}/{total:2} passed")

    print(f"\n{Colors.BOLD}Total Unofficial:{Colors.END}")
    print(f"  Total:  {total_passed + total_failed}")
    print_success(f"  Passed: {total_passed}")
    if total_failed > 0:
        print_error(f"  Failed: {total_failed}")

    return total_passed, total_failed


def main():
    parser = argparse.ArgumentParser(description="Run Ex4 test suite")
    parser.add_argument('--official', action='store_true', help='Run only official tests')
    parser.add_argument('--unofficial', action='store_true', help='Run only unofficial tests')
    parser.add_argument('--category', type=str, help='Run specific category (e.g., global, local)')
    parser.add_argument('--zip', type=str, help='Test a submission zip file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    temp_dir_obj = None
    executable_path = None

    try:
        # Handle submission zip file
        if args.zip:
            print_header("EX4 TEST SUITE RUNNER - SUBMISSION MODE")

            # Create temporary directory
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = pathlib.Path(temp_dir_obj.name)

            # Extract submission
            ex4_dir, ids_file = extract_submission_zip(args.zip, temp_dir)
            if ex4_dir is None:
                return 1

            # Build ANALYZER
            executable_path = build_analyzer_from_submission(ex4_dir)
            if executable_path is None:
                return 1

        else:
            # Normal mode - use local ex4 directory
            executable_path = check_analyzer_exists()
            if not executable_path:
                return 1

            print_header("EX4 TEST SUITE RUNNER")
            print(f"Analyzer: {executable_path}")

        total_passed = 0
        total_failed = 0

        # Determine what to run
        run_official = not args.unofficial or args.official
        run_unofficial = not args.official or args.unofficial

        if args.category:
            if args.category not in CATEGORIES:
                print_error(f"Invalid category: {args.category}")
                print(f"Valid categories: {', '.join(CATEGORIES)}")
                return 1
            run_official = False
            run_unofficial = True

        # Run tests
        if run_official:
            passed, failed = run_official_tests(executable_path, args.verbose)
            total_passed += passed
            total_failed += failed

        if run_unofficial:
            passed, failed = run_unofficial_tests(executable_path, args.category, args.verbose)
            total_passed += passed
            total_failed += failed

        # Overall summary
        print_header("OVERALL SUMMARY")
        print(f"Total tests:  {total_passed + total_failed}")
        print_success(f"Passed:       {total_passed}")
        if total_failed > 0:
            print_error(f"Failed:       {total_failed}")
        else:
            print_success("\n✓ ALL TESTS PASSED!")

        return 0 if total_failed == 0 else 1

    finally:
        # Cleanup temporary directory if created
        if temp_dir_obj:
            temp_dir_obj.cleanup()


if __name__ == "__main__":
    sys.exit(main())
