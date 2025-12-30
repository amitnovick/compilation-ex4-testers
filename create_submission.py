#!/usr/bin/env python3
"""
Create Submission Zip for Ex4

Creates a submission zip file according to ex4.md requirements:
- Zip file named <ID>.zip (where ID is student ID)
- Contains ids.txt with team member IDs
- Contains ex4/ directory with all source code and Makefile

Usage:
    python3 create_submission.py /path/to/ex4/directory
    python3 create_submission.py /path/to/ex4/directory --id 123456789
    python3 create_submission.py /path/to/ex4/directory --ids 111111111 222222222
"""

import os
import sys
import shutil
import zipfile
import pathlib
import argparse
import tempfile


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def validate_student_ids(ids):
    """Validate student IDs (should be numeric)"""
    valid_ids = []
    for student_id in ids:
        student_id = student_id.strip()
        if not student_id:
            continue
        if not student_id.isdigit():
            print_warning(f"ID '{student_id}' is not numeric, skipping")
            continue
        valid_ids.append(student_id)
    return valid_ids


def get_student_ids_interactive():
    """Interactively get student IDs from user"""
    print_info("Enter student IDs (one per line, empty line to finish):")
    ids = []
    while True:
        try:
            student_id = input(f"  ID {len(ids)+1}: ").strip()
            if not student_id:
                break
            if not student_id.isdigit():
                print_warning("ID must be numeric")
                continue
            ids.append(student_id)
        except (KeyboardInterrupt, EOFError):
            print()
            break

    return ids


# Paths required for the Makefile to build (whitelist approach)
REQUIRED_PATHS = [
    'Makefile',
    'manifest',
    'jflex',
    'cup',
    'external_jars',
    'src',
]

# Patterns to ignore even within required directories
IGNORE_PATTERNS = [
    '*.class', '*.o', '*.so', '*.a',
    '__pycache__', '.git', '.gitignore',
    '*.swp', '*.swo', '.DS_Store',
    'ANALYZER',
]


def copy_required_files(src_dir, dest_dir, required_paths, ignore_patterns):
    """
    Copy only required paths from src to dest.

    Args:
        src_dir: Source directory (Path)
        dest_dir: Destination directory (Path)
        required_paths: List of relative paths to include
        ignore_patterns: List of patterns to ignore
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    for path in required_paths:
        src_path = src_dir / path
        dest_path = dest_dir / path

        if not src_path.exists():
            continue

        if src_path.is_file():
            shutil.copy2(src_path, dest_path)
        elif src_path.is_dir():
            shutil.copytree(src_path, dest_path,
                           ignore=shutil.ignore_patterns(*ignore_patterns))


def validate_ex4_directory(ex4_path):
    """
    Validate that the directory contains required files
    Returns: (is_valid, error_message)
    """
    if not ex4_path.exists():
        return False, f"Directory does not exist: {ex4_path}"

    if not ex4_path.is_dir():
        return False, f"Path is not a directory: {ex4_path}"

    # Check for Makefile
    makefile = ex4_path / 'Makefile'
    if not makefile.exists():
        return False, "Makefile not found in ex4 directory"

    # Check for source files (at least one .java file or similar)
    source_files = list(ex4_path.glob('**/*.java')) + \
                   list(ex4_path.glob('**/*.py')) + \
                   list(ex4_path.glob('**/*.cpp')) + \
                   list(ex4_path.glob('**/*.c'))

    if not source_files:
        print_warning("No source files (.java, .py, .cpp, .c) found in directory")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return False, "No source files found"

    return True, None


def create_submission_zip(ex4_path, student_ids, output_dir=None):
    """
    Create submission zip file

    Args:
        ex4_path: Path to ex4 directory
        student_ids: List of student IDs
        output_dir: Output directory for zip file (default: current directory)

    Returns:
        Path to created zip file
    """
    if not student_ids:
        raise ValueError("At least one student ID is required")

    # Use first student ID for zip file name
    primary_id = student_ids[0]

    # Determine output directory
    if output_dir is None:
        output_dir = pathlib.Path.cwd()
    else:
        output_dir = pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"{primary_id}.zip"
    zip_path = output_dir / zip_filename

    # Create temporary directory for staging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)

        # Create ids.txt
        ids_file = temp_path / 'ids.txt'
        with open(ids_file, 'w') as f:
            for student_id in student_ids:
                f.write(f"{student_id}\n")
        print_success(f"Created ids.txt with {len(student_ids)} ID(s)")

        # Copy only required files (whitelist approach)
        ex4_dest = temp_path / 'ex4'
        print_info(f"Copying required files from {ex4_path}...")
        copy_required_files(ex4_path, ex4_dest, REQUIRED_PATHS, IGNORE_PATTERNS)
        print_success("Copied required files")

        # Create zip file
        print_info(f"Creating {zip_filename}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add ids.txt
            zipf.write(ids_file, 'ids.txt')

            # Add ex4 directory recursively
            for file_path in ex4_dest.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)

        print_success(f"Created {zip_filename}")

    return zip_path


def verify_zip_contents(zip_path):
    """Verify the contents of the created zip file"""
    print_info(f"Verifying {zip_path.name}...")

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()

        # Check for ids.txt
        if 'ids.txt' not in file_list:
            print_error("ids.txt not found in zip")
            return False

        # Check for ex4/ directory
        ex4_files = [f for f in file_list if f.startswith('ex4/')]
        if not ex4_files:
            print_error("ex4/ directory not found in zip")
            return False

        # Check for Makefile
        if 'ex4/Makefile' not in file_list:
            print_error("ex4/Makefile not found in zip")
            return False

        print_success("Zip structure validated:")
        print(f"  ✓ ids.txt")
        print(f"  ✓ ex4/ directory with {len(ex4_files)} files")
        print(f"  ✓ ex4/Makefile")

        # Show ids.txt content
        with zipf.open('ids.txt') as f:
            ids_content = f.read().decode('utf-8')
            print(f"\n  Student IDs:")
            for line in ids_content.strip().split('\n'):
                print(f"    - {line}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Create submission zip file for Ex4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (will prompt for IDs)
  python3 create_submission.py ~/Dropbox/dev/tau/compilation/ex4

  # Single student
  python3 create_submission.py ~/Dropbox/dev/tau/compilation/ex4 --id 123456789

  # Team submission
  python3 create_submission.py ~/Dropbox/dev/tau/compilation/ex4 --ids 111111111 222222222

  # Specify output directory
  python3 create_submission.py ~/Dropbox/dev/tau/compilation/ex4 --id 123456789 --output ~/submissions
        """
    )

    parser.add_argument('ex4_directory', type=str,
                       help='Path to ex4 directory containing source code and Makefile')
    parser.add_argument('--id', type=str,
                       help='Single student ID')
    parser.add_argument('--ids', nargs='+', type=str,
                       help='Multiple student IDs (for team submission)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output directory for zip file (default: current directory)')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Overwrite existing zip file without prompting')

    args = parser.parse_args()

    print_header("EX4 SUBMISSION ZIP CREATOR")

    # Resolve ex4 directory path
    ex4_path = pathlib.Path(args.ex4_directory).expanduser().resolve()
    print_info(f"Ex4 directory: {ex4_path}")

    # Validate ex4 directory
    is_valid, error_msg = validate_ex4_directory(ex4_path)
    if not is_valid:
        print_error(f"Invalid ex4 directory: {error_msg}")
        return 1

    print_success("Ex4 directory validated")

    # Get student IDs
    student_ids = []
    if args.id:
        student_ids = [args.id]
    elif args.ids:
        student_ids = args.ids
    else:
        # Interactive mode
        student_ids = get_student_ids_interactive()

    # Validate IDs
    student_ids = validate_student_ids(student_ids)

    if not student_ids:
        print_error("No valid student IDs provided")
        return 1

    print_info(f"Student IDs: {', '.join(student_ids)}")

    # Determine output directory
    output_dir = pathlib.Path(args.output).expanduser() if args.output else pathlib.Path.cwd()
    zip_filename = f"{student_ids[0]}.zip"
    zip_path = output_dir / zip_filename

    # Check if zip already exists
    if zip_path.exists() and not args.force:
        print_warning(f"Zip file already exists: {zip_path}")
        response = input("Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print_info("Aborted")
            return 0

    # Create submission zip
    try:
        zip_path = create_submission_zip(ex4_path, student_ids, output_dir)
    except Exception as e:
        print_error(f"Failed to create zip file: {e}")
        return 1

    # Verify zip contents
    if not verify_zip_contents(zip_path):
        print_error("Zip verification failed")
        return 1

    # Show final result
    print_header("SUBMISSION READY")
    print_success(f"Zip file created: {zip_path}")
    print_info(f"File size: {zip_path.stat().st_size / 1024:.1f} KB")

    print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
    print(f"  1. Test with self-check.py on nova.cs.tau.ac.il")
    print(f"  2. Submit {zip_filename}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
