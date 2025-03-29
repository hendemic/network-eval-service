#!/usr/bin/env python3
"""
Runner for end-to-end tests
Uses the same colored testing framework as the unit tests
"""
import unittest
import os
import sys
import time
import io
from contextlib import redirect_stdout

# Add project root to the path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import colored test runner components from unit test runner
from tests.run_unit_tests import Colors, ColoredTestResult, ColoredTestRunner

if __name__ == "__main__":
    print(f"{Colors.BLUE}{Colors.BOLD}Running End-to-End Tests{Colors.ENDC}")
    print(f"{Colors.YELLOW}Note: These tests may take longer to run as they test the full system workflow{Colors.ENDC}")
    print("")
    
    # Find all tests in the end-to-end-tests directory
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "end-to-end-tests")
    
    # Use the test loader to find all tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    
    # Buffer stdout to prevent test output from mixing with our summary
    buffer = io.StringIO()
    
    # Determine verbosity
    verbose_mode = '-v' in sys.argv or '--verbose' in sys.argv
    
    # Run the tests with our colored runner, capturing output
    with redirect_stdout(buffer):
        # Use higher verbosity in verbose mode
        runner = ColoredTestRunner(verbosity=2 if verbose_mode else 1)
        result = runner.run(suite)
    
    # Print captured output if tests fail or if verbose flag is provided
    if verbose_mode or not result.wasSuccessful():
        print("\n--- Captured Test Output ---")
        print(buffer.getvalue())
    
    # Return non-zero exit code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)