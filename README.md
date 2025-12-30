# Ex4 Uninitialized Variable Analysis - Test Suite

Comprehensive test suite for Exercise 4's uninitialized variable analysis.

## Directory Structure

```
ex4-tests/
├── official/                      # Pre-existing official tests (2 tests)
│   ├── tests/
│   │   ├── TEST_1.txt
│   │   └── TEST_2.txt
│   └── expected_output/
│       ├── TEST_1_Expected_Output.txt
│       └── TEST_2_Expected_Output.txt
│
├── unofficial/                    # Comprehensive test suite (62 tests)
│   ├── global/                   # Global variable tests (10)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── local/                    # Local variable tests (8)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── propagation/              # Value propagation tests (6)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── shadow/                   # Variable shadowing tests (6)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── if/                       # If control flow tests (6)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── while/                    # While control flow tests (6)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── printint/                 # PrintInt function tests (4)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── expr/                     # Complex expression tests (4)
│   │   ├── tests/
│   │   └── expected_output/
│   ├── edge/                     # Edge case tests (6)
│   │   ├── tests/
│   │   └── expected_output/
│   └── ok/                       # Valid program tests (6)
│       ├── tests/
│       └── expected_output/
│
├── run_tests.py                  # New test runner (runs both official & unofficial)
└── create_submission.py          # Create submission zip file from code directory
```



## Running Tests

### Create Submission Zip File

This will:
- Select all files of the exercise from directory at <PATH_TO_DIR> and create Zip file from them

#### Single Student

```bash
python3 create_submission.py <PATH_TO_DIR> --id <ID>
```

#### Team Submission

```bash
python3 create_submission.py <PATH_TO_DIR> --ids <ID1> <ID2>
```


### Test a Submission Zip File

```bash
# Test a submission zip (automatically extracts, builds, and tests)
python3 run_tests.py --zip <ID1>.zip
```

This will:
1. Extract the zip file to a temporary directory
2. Validate the structure (ids.txt, ex4/, Makefile)
3. Build the ANALYZER using make
4. Run all tests against the built analyzer
5. Clean up temporary files automatically

## Test Categories

### 1. Global Variables (10 tests)
Tests global variable initialization semantics before main() executes.

- Single uninitialized global
- Multiple uninitialized globals
- Valid initialization chains
- Invalid initialization chains (propagation)
- Initialization order (globals declared after main)
- Self-referential initialization

### 2. Local Variables (8 tests)
Tests local variable initialization within main().

- Single/multiple uninitialized locals
- Initialization from constants
- Initialization from globals
- Declared but unused variables
- Chain propagation

### 3. Value Propagation (6 tests)
Tests how uninitialized status propagates through assignments.

- Reassignment clearing uninit status
- Reassignment from uninit tainting target
- Multi-level propagation chains
- Self-assignment when uninit

### 4. Variable Shadowing (6 tests)
Tests scope handling when locals shadow globals.

- Local uninit, global init (Figure 4 pattern)
- Local init, global uninit
- Both uninit/both init
- Multiple variables with different shadow states

### 5. If Control Flow (6 tests)
Tests conservative analysis for if statements (body may not execute).

- Variable initialized only in if body
- Uninitialized variable in condition
- No else branch
- Nested if statements

### 6. While Control Flow (6 tests)
Tests conservative analysis for while loops (body may never execute).

- Variable initialized only in while body
- Uninitialized variable in condition
- Nested while loops
- Variable initialized before loop

### 7. PrintInt Function (4 tests)
Tests PrintInt() argument validation.

- Uninitialized argument
- Initialized argument
- Propagated uninitialized value
- Multiple PrintInt calls

### 8. Complex Expressions (4 tests)
Tests detection in nested expressions.

- All variables initialized
- One uninitialized among many
- Multiple uninitialized
- Nested parentheses

### 9. Edge Cases (6 tests)
Tests boundary conditions.

- Empty main function
- Only declarations (never used)
- Only globals, empty main
- No globals, only locals
- Same variable used multiple times (listed once)
- Alphabetical sorting (ASCII order)

### 10. Valid Programs (6 tests)
Tests that valid programs produce "!OK" (no false positives).

- Figure 5 from ex4.md
- All variables initialized before use
- Reassignment before use
- Complex control flow
- Unused uninitialized variables

## Expected Output Format

### Valid Programs
```
!OK
```

### Programs with Uninitialized Access
```
variable1
variable2
variable3
```

## Test Statistics

| Suite | Tests | Coverage |
|-------|-------|----------|
| Official | 2 | Pre-existing tests |
| Unofficial | 62 | Comprehensive coverage |
| **Total** | **64** | **All ex4 scenarios** |

### Unofficial Breakdown

| Category | Count | Focus |
|----------|-------|-------|
| Global Variables | 10 | Global initialization |
| Local Variables | 8 | Local initialization |
| Value Propagation | 6 | Uninit propagation |
| Variable Shadowing | 6 | Scope handling |
| If Control Flow | 6 | Conservative if analysis |
| While Control Flow | 6 | Conservative while analysis |
| PrintInt | 4 | Function argument validation |
| Complex Expressions | 4 | Nested expressions |
| Edge Cases | 6 | Boundary conditions |
| Valid Programs | 6 | No false positives |

## Example Usage

```bash
python3 create_submission.py /path/to/ex4 --id 123456789

python3 run_tests.py --zip 123456789.zip

# Expected output:
# ======================================================================
#                          EX4 TEST SUITE RUNNER
# ======================================================================
#
# Analyzer: /path/to/ex4
#
# ======================================================================
#                             OFFICIAL TESTS
# ======================================================================
#
# Running TEST_1... ✓ PASS
# Running TEST_2... ✓ PASS
#
# Official Tests Summary:
#   Total:  2
#   Passed: 2
#
# ======================================================================
#                           UNOFFICIAL TESTS
# ======================================================================
#
# Category: GLOBAL
#   Running TEST_global_single_uninit... ✓ PASS
#   Running TEST_global_multiple_uninit... ✓ PASS
#   ...
#   global: 10/10 passed
#
# [... other categories ...]
#
# Unofficial Tests Summary:
#   global       10/10 passed
#   local         8/8 passed
#   propagation   6/6 passed
#   shadow        6/6 passed
#   if            6/6 passed
#   while         6/6 passed
#   printint      4/4 passed
#   expr          4/4 passed
#   edge          6/6 passed
#   ok            6/6 passed
#
# Total Unofficial:
#   Total:  62
#   Passed: 62
#
# ======================================================================
#                          OVERALL SUMMARY
# ======================================================================
#
# Total tests:  64
# Passed:       64
#
# ✓ ALL TESTS PASSED!
```

## Debugging Failed Tests

If a test fails, use verbose mode to see the output comparison:

```bash
python3 run_tests.py --category global -v
```

This will show:
```
Expected: 'g\n'
Actual:   'OK\n'
```

## Adding New Tests

To add new tests to the unofficial suite:

1. Choose appropriate category (or create new one)
2. Create test file: `unofficial/<category>/tests/TEST_<category>_<description>.txt`
3. Create expected output: `unofficial/<category>/expected_output/TEST_<category>_<description>_Expected_Output.txt`
4. Run: `python3 run_tests.py --category <category>`

## Creating Submission Zip


### Custom Output Directory

```bash
python3 create_submission.py ~/path/to/ex4 --id 123456789 --output ~/submissions
```

### What It Does

1. Validates the ex4 directory (checks for Makefile and source files)
2. Creates `ids.txt` with student IDs
3. Copies ex4 directory (excluding build artifacts: *.class, *.o, ANALYZER, etc.)
4. Creates `<ID>.zip` with proper structure:
   ```
   <ID>.zip
   ├── ids.txt
   └── ex4/
       ├── Makefile
       └── [source files]
   ```
5. Verifies zip contents

### Example Output

```
======================================================================
                      EX4 SUBMISSION ZIP CREATOR
======================================================================

ℹ Ex4 directory: /home/user/ex4
✓ Ex4 directory validated
ℹ Student IDs: 123456789
✓ Created ids.txt with 1 ID(s)
✓ Copied ex4 directory
✓ Created 123456789.zip
ℹ Verifying 123456789.zip...
✓ Zip structure validated:
  ✓ ids.txt
  ✓ ex4/ directory with 25 files
  ✓ ex4/Makefile

  Student IDs:
    - 123456789

======================================================================
                        SUBMISSION READY
======================================================================

✓ Zip file created: /home/user/123456789.zip
ℹ File size: 45.3 KB

Next steps:
  1. Test with self-check.py on nova.cs.tau.ac.il
  2. Submit 123456789.zip
```

## Notes

- The `run_tests.py` script is for **development testing** (works with reorganized structure)
- The `create_submission.py` script is for **creating submission zip files** from ex4 directory
- All scripts expect the ANALYZER executable at `ex4/ANALYZER` (built by Makefile)
