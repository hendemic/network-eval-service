#!/usr/bin/env python3
"""
Network test scheduler using APScheduler
Runs the network test at regular intervals
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
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        logger.error(f"Could not find file: {file_path}")
        return None
    
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing module {module_name}: {e}")
        return None

def run_test():
    """Run the network test"""
    try:
        logger.info(f"Running network test at {datetime.now().isoformat()}")
        
        # Import the run_test module
        run_test_module = import_module_from_file('run_test', RUN_TEST_PATH)
        
        if run_test_module and hasattr(run_test_module, 'main'):
            # Execute the main function
            run_test_module.main()
            logger.info("Network test completed successfully")
        else:
            logger.error("Could not find main function in run_test module")
    except Exception as e:
        logger.error(f"Error running network test: {e}")

def main():
    """Main function to start the scheduler"""
    # Get test interval from environment
    interval_seconds = float(os.environ.get('TEST_INTERVAL_SECONDS', '60'))
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