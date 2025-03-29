#!/usr/bin/env python3
"""
Test runner for unit tests with color-coded results
"""
import unittest
import os
import sys
import time
import io
from contextlib import redirect_stdout

# Add project root to the path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColoredTestResult(unittest.TextTestResult):
    """Custom TestResult class that provides color-coded output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.verbosity = verbosity
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.skip_count = 0
        self.test_results = []
        self.start_time = time.time()
    
    def startTest(self, test):
        super().startTest(test)
        if self.verbosity > 1:
            test_name = self.getDescription(test)
            docstring = test._testMethodDoc or ""
            if docstring:
                docstring = f" - {docstring}"
                
            self.stream.write(f"\n{Colors.BLUE}{Colors.BOLD}Running: {test_name}{Colors.ENDC}{docstring}\n")
            self.stream.flush()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.write(f"  {Colors.GREEN}✓ PASS{Colors.ENDC}\n")
        self.test_results.append((test, "PASS"))
    
    def addError(self, test, err):
        super().addError(test, err)
        self.error_count += 1
        if self.verbosity > 1:
            self.stream.write(f"  {Colors.RED}✗ ERROR{Colors.ENDC}\n")
        self.test_results.append((test, "ERROR"))
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failure_count += 1
        if self.verbosity > 1:
            self.stream.write(f"  {Colors.RED}✗ FAIL{Colors.ENDC}\n")
        self.test_results.append((test, "FAIL"))
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.skip_count += 1
        if self.verbosity > 1:
            self.stream.write(f"  {Colors.YELLOW}⚠ SKIP ({reason}){Colors.ENDC}\n")
        self.test_results.append((test, "SKIP"))

    def printSummary(self):
        """Print a nice summary of test results"""
        elapsed_time = time.time() - self.start_time
        self.stream.writeln("\n" + "="*80)
        self.stream.writeln(f"{Colors.BOLD}TEST RESULTS SUMMARY{Colors.ENDC}")
        self.stream.writeln("="*80)
        
        for test, result in self.test_results:
            test_name = test.id()
            if result == "PASS":
                status = f"{Colors.GREEN}PASS{Colors.ENDC}"
            elif result == "FAIL":
                status = f"{Colors.RED}FAIL{Colors.ENDC}"
            elif result == "ERROR":
                status = f"{Colors.RED}ERROR{Colors.ENDC}"
            else:
                status = f"{Colors.YELLOW}SKIP{Colors.ENDC}"
            
            self.stream.writeln(f"{test_name:<70} {status}")
        
        self.stream.writeln("-"*80)
        total = self.success_count + self.failure_count + self.error_count + self.skip_count
        
        # Summary line with color based on result
        if self.wasSuccessful():
            summary_color = Colors.GREEN
        else:
            summary_color = Colors.RED
            
        self.stream.writeln(f"{summary_color}{Colors.BOLD}TOTAL: {total} tests, "
                      f"{self.success_count} passed, "
                      f"{self.failure_count} failed, "
                      f"{self.error_count} errors, "
                      f"{self.skip_count} skipped "
                      f"({elapsed_time:.3f}s){Colors.ENDC}")
        self.stream.writeln("="*80)

class ColoredTestRunner(unittest.TextTestRunner):
    """Custom TestRunner using ColoredTestResult"""
    resultclass = ColoredTestResult
    
    def run(self, test):
        result = super().run(test)
        result.printSummary()
        return result

if __name__ == "__main__":
    # Find all tests in the unit-tests directory
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unit-tests")
    
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