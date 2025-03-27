#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from flask import Flask

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, PingResult
from backend.config import config
from backend.pingTest import ping_test

def run_network_test():
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Run ping test
        test_results = ping_test(
            target=app.config['TEST_TARGET'],
            count=app.config['TEST_COUNT'],
            interval=app.config['TEST_INTERVAL']
        )
        
        if not test_results:
            print("Test failed or was aborted.")
            return
        
        # Create a new record
        ping_record = PingResult(
            timestamp=test_results['timestamp'],
            target=test_results['target'],
            packet_loss=test_results['packet_loss'],
            min_latency=test_results['min_latency'],
            max_latency=test_results['max_latency'],
            avg_latency=test_results['avg_latency'],
            jitter=test_results['jitter'],
            packets_sent=test_results['packets_sent'],
            packets_received=test_results['packets_received']
        )
        
        # Save to database
        try:
            db.session.add(ping_record)
            db.session.commit()
            print(f"Saved ping test results to database at {datetime.now()}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving results: {str(e)}")

if __name__ == '__main__':
    run_network_test()