#!/usr/bin/env python3
"""
Network Test Scheduler for the Network Evaluation Service

This module provides a reliable scheduling system for executing network tests
at regular intervals. It uses APScheduler to ensure tests continue running
even after temporary failures, maintaining consistent monitoring.

Key features:
- Configurable test intervals via environment variables
- Automatic recovery from test failures
- Logging of test execution and results
- Dynamic loading of the test module
"""
import os
import sys
import logging
import importlib.util
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('network-test-scheduler')

# Path to run_test.py
RUN_TEST_PATH = '/app/backend/run_test.py'

def import_module_from_file(module_name, file_path):
    """Dynamically import a Python module from a file path.
    
    This function allows the scheduler to load the test module at runtime
    without requiring it to be in the Python path. This enables a more
    flexible container architecture where modules can be mounted at runtime.
    
    Args:
        module_name: The name to assign to the imported module
        file_path: The absolute path to the Python file to import
        
    Returns:
        The imported module object, or None if import failed
    """
    # Create a module spec from the file path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        logger.error(f"Could not find file: {file_path}")
        return None
    
    # Create a module from the spec
    module = importlib.util.module_from_spec(spec)
    try:
        # Execute the module code in the module's namespace
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing module {module_name}: {e}")
        return None

def run_test():
    """Execute a network test by dynamically loading and running the test module.
    
    This function:
    1. Imports the test module from the specified path
    2. Calls its main() function to run the test
    3. Logs the outcome (success or failure)
    
    The test module is responsible for:
    - Creating a database connection
    - Running the actual ping test
    - Storing results in the database
    """
    try:
        # Log test start with ISO-formatted timestamp for easier log parsing
        logger.info(f"Running network test at {datetime.now().isoformat()}")
        
        # Dynamically import the test module from its file path
        # This allows for easy updates without restarting the container
        run_test_module = import_module_from_file('run_test', RUN_TEST_PATH)
        
        # Verify the module was loaded and has the expected entry point
        if run_test_module and hasattr(run_test_module, 'main'):
            # Execute the test by calling its main function
            run_test_module.main()
            logger.info("Network test completed successfully")
        else:
            logger.error("Could not find main function in run_test module")
    except Exception as e:
        # Catch and log any exception to prevent the scheduler from crashing
        logger.error(f"Error running network test: {e}")

def main():
    """Initialize and start the test scheduler.
    
    This function:
    1. Reads configuration from environment variables
    2. Sets up a recurring job to execute network tests
    3. Keeps the scheduler running until process termination
    """
    # Get test interval from environment variables with a sensible default
    interval_seconds = float(os.environ.get('TEST_INTERVAL', '60'))
    logger.info(f"Starting scheduler with interval: {interval_seconds} seconds")
    
    # Create the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_test, 'interval', seconds=interval_seconds, 
                      next_run_time=datetime.now())
    
    try:
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to exit")
        
        # Run once immediately
        logger.info("Running initial test...")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()

if __name__ == "__main__":
    main()