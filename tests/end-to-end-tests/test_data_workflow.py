#!/usr/bin/env python3
"""
End-to-End test for Network Evaluation Service

Tests the entire data flow from:
1. Ping data collection
2. Database storage
3. Data retrieval
4. API response format (simulating what would be visualized)
"""
import unittest
import sys
import os
import time
import datetime
from unittest.mock import patch

# Add project root to the path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import application modules
from backend.app import create_app
from backend.models import db, PingResult
from backend.pingTest import ping_test
from backend.run_test import run_network_test

class TestEndToEndWorkflow(unittest.TestCase):
    """Test the complete workflow from ping data collection to retrieval"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test Flask app using the testing configuration
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create the database tables
        db.create_all()
        
        # Create a test client
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Clean up after test"""
        # Clean up database
        db.session.remove()
        db.drop_all()
        
        # Remove app context
        self.app_context.pop()
    
    def test_ping_data_collection_to_storage(self):
        """Test that ping data can be collected and stored in the database"""
        # Mock the ping subprocess call
        with patch('backend.pingTest.subprocess.Popen') as mock_popen:
            # Mock the ping subprocess output to return a consistent result
            mock_process = mock_popen.return_value
            mock_process.stdout.readline.side_effect = [
                "64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=10.5 ms",
                "64 bytes from 1.1.1.1: icmp_seq=2 ttl=57 time=12.3 ms",
                "64 bytes from 1.1.1.1: icmp_seq=3 ttl=57 time=11.8 ms",
                "64 bytes from 1.1.1.1: icmp_seq=4 ttl=57 time=timeout",  # Simulate a timeout
                "64 bytes from 1.1.1.1: icmp_seq=5 ttl=57 time=9.7 ms",
                ""  # End of output
            ]
            
            # Set a small TEST_COUNT for faster testing
            original_test_count = self.app.config['TEST_COUNT']
            self.app.config['TEST_COUNT'] = 5
            
            try:
                # Capture the database state before running the test
                count_before = PingResult.query.count()
                
                # Directly call the ping_test function and store the results
                # instead of using run_network_test() which creates its own Flask app
                test_results = ping_test(
                    target=self.app.config['TEST_TARGET'],
                    count=self.app.config['TEST_COUNT'],
                    interval=self.app.config['TEST_INTERVAL']
                )
                
                # Create and save a new ping result
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
                
                db.session.add(ping_record)
                db.session.commit()
            finally:
                # Restore original config
                self.app.config['TEST_COUNT'] = original_test_count
        
        # Check that a new record was added to the database
        count_after = PingResult.query.count()
        self.assertEqual(count_after, count_before + 1, 
                         "A new ping result should have been added to the database")
        
        # Get the latest record
        latest_result = PingResult.query.order_by(PingResult.timestamp.desc()).first()
        
        # Verify that the ping result has the expected data 
        # (based on our mocked ping responses above)
        self.assertIsNotNone(latest_result)
        self.assertEqual(latest_result.target, self.app.config['TEST_TARGET'])
        self.assertEqual(latest_result.packets_sent, 5)
        self.assertEqual(latest_result.packets_received, 4)  # One timeout
        self.assertEqual(latest_result.packet_loss, 20.0)  # 1 out of 5 = 20%
        
        # Check the latency values match our mock data
        self.assertAlmostEqual(latest_result.min_latency, 9.7, places=1)
        self.assertAlmostEqual(latest_result.max_latency, 12.3, places=1)
        
        # Expected average: (10.5 + 12.3 + 11.8 + 9.7) / 4 = 11.075
        self.assertAlmostEqual(latest_result.avg_latency, 11.075, places=1)
        
        # Expected jitter: average of absolute differences between consecutive packets
        # |12.3 - 10.5| + |11.8 - 12.3| + |9.7 - 11.8| = 1.8 + 0.5 + 2.1 = 4.4 / 3 = 1.467
        self.assertGreater(latest_result.jitter, 0)
    
    def test_data_retrieval_api(self):
        """Test that stored ping data can be retrieved via the API"""
        # Create test data with known values
        for i in range(3):
            # Create test results at different times
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=10*i)
            ping_result = PingResult(
                timestamp=timestamp,
                target="8.8.8.8",
                packet_loss=i*2.0,  # 0%, 2%, 4%
                min_latency=10.0 + i,  # 10, 11, 12
                max_latency=15.0 + i,  # 15, 16, 17
                avg_latency=12.5 + i,  # 12.5, 13.5, 14.5
                jitter=1.5,
                packets_sent=100,
                packets_received=100 - (i*2)  # 100, 98, 96
            )
            db.session.add(ping_result)
        
        db.session.commit()
        
        # Test API endpoint for ping results
        response = self.client.get('/api/ping-results?hours=1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # All results should be within the last hour since they're only 10 minutes apart
        self.assertEqual(len(data), 3)
        
        # Results should be ordered newest first
        newest = data[0]
        self.assertEqual(newest['target'], "8.8.8.8")
        self.assertEqual(newest['packet_loss'], 0.0)
        self.assertEqual(newest['min_latency'], 10.0)
        self.assertEqual(newest['max_latency'], 15.0)
        self.assertEqual(newest['avg_latency'], 12.5)
        
        # Test with a longer time window to get all results
        response = self.client.get('/api/ping-results?hours=24')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # All three results should be returned, newest first
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['packet_loss'], 0.0)  # Newest result
        self.assertEqual(data[1]['packet_loss'], 2.0)  # Middle result
        self.assertEqual(data[2]['packet_loss'], 4.0)  # Oldest result
    
    def test_ping_stats_api(self):
        """Test the ping stats API endpoint with stored test data"""
        # Create test data for the last 24 hours
        for i in range(5):
            # Create test results at different times
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=i*4)
            ping_result = PingResult(
                timestamp=timestamp,
                target="8.8.8.8",
                packet_loss=i*1.0,  # 0%, 1%, 2%, 3%, 4%
                min_latency=10.0 - i*0.5,  # 10, 9.5, 9, 8.5, 8
                max_latency=20.0 + i,  # 20, 21, 22, 23, 24
                avg_latency=15.0 + i*0.5,  # 15, 15.5, 16, 16.5, 17
                jitter=1.0 + i*0.2,  # 1.0, 1.2, 1.4, 1.6, 1.8
                packets_sent=100,
                packets_received=100 - i  # 100, 99, 98, 97, 96
            )
            db.session.add(ping_result)
        
        db.session.commit()
        
        # Test the ping stats API endpoint
        response = self.client.get('/api/ping-stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Verify the structure and contents of the response
        self.assertIn('latest', data)
        self.assertIn('day_stats', data)
        
        # Latest should be the most recent result (i=0)
        self.assertEqual(data['latest']['packet_loss'], 0.0)
        self.assertEqual(data['latest']['min_latency'], 10.0)
        self.assertEqual(data['latest']['max_latency'], 20.0)
        self.assertEqual(data['latest']['avg_latency'], 15.0)
        self.assertEqual(data['latest']['jitter'], 1.0)
        
        # Check day stats (averages of all 5 results)
        # Expected day stats averages:
        # packet_loss: (0 + 1 + 2 + 3 + 4) / 5 = 2.0
        # max_packet_loss: 4.0 (highest of all)
        # avg_latency: (15 + 15.5 + 16 + 16.5 + 17) / 5 = 16.0
        # jitter: (1.0 + 1.2 + 1.4 + 1.6 + 1.8) / 5 = 1.4
        self.assertAlmostEqual(data['day_stats']['avg_packet_loss'], 2.0, places=1)
        self.assertAlmostEqual(data['day_stats']['max_packet_loss'], 4.0, places=1)
        self.assertAlmostEqual(data['day_stats']['avg_latency'], 16.0, places=1)
        self.assertAlmostEqual(data['day_stats']['avg_jitter'], 1.4, places=1)
        
        # min_latency should be the minimum of all min_latency values (8.0)
        self.assertEqual(data['day_stats']['min_latency'], 8.0)
        
        # max_latency should be the maximum of all max_latency values (24.0)
        self.assertEqual(data['day_stats']['max_latency'], 24.0)
    
    def test_full_workflow(self):
        """Test the complete workflow from ping collection to API response"""
        # Mock the ping subprocess call
        with patch('backend.pingTest.subprocess.Popen') as mock_popen:
            # Mock the ping subprocess output
            mock_process = mock_popen.return_value
            mock_process.stdout.readline.side_effect = [
                "64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=15.5 ms",
                "64 bytes from 1.1.1.1: icmp_seq=2 ttl=57 time=17.3 ms",
                "64 bytes from 1.1.1.1: icmp_seq=3 ttl=57 time=16.8 ms",
                ""  # End of output
            ]
            
            # Set a small TEST_COUNT for faster testing
            original_test_count = self.app.config['TEST_COUNT']
            self.app.config['TEST_COUNT'] = 3
            
            try:
                # Step 1: Collect ping data and directly store it 
                # (skip run_network_test which creates its own Flask app)
                test_results = ping_test(
                    target=self.app.config['TEST_TARGET'],
                    count=self.app.config['TEST_COUNT'],
                    interval=self.app.config['TEST_INTERVAL']
                )
                
                # Create and save a new ping result
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
                
                db.session.add(ping_record)
                db.session.commit()
            finally:
                # Restore original config
                self.app.config['TEST_COUNT'] = original_test_count
        
        # Verify data was stored in the database
        result_count = PingResult.query.count()
        self.assertTrue(result_count > 0, "Database should contain at least one record")
        
        # Step 2: Query the data via the API endpoints
        # Test the ping-results API - use a larger window to make sure we catch the data
        response = self.client.get('/api/ping-results?hours=24')
        self.assertEqual(response.status_code, 200)
        results_data = response.get_json()
        self.assertTrue(len(results_data) > 0, "API should return at least one result")
        
        # Step 3: Test the ping-stats API
        response = self.client.get('/api/ping-stats')
        self.assertEqual(response.status_code, 200)
        stats_data = response.get_json()
        
        # Verify the data matches what we expect from our mock
        self.assertEqual(stats_data['latest']['packets_sent'], 3)
        self.assertEqual(stats_data['latest']['packets_received'], 3)
        self.assertEqual(stats_data['latest']['packet_loss'], 0.0)
        
        # Expected values from our mock ping responses
        # min_latency: 15.5
        # max_latency: 17.3
        # avg_latency: (15.5 + 17.3 + 16.8) / 3 = 16.533
        self.assertAlmostEqual(stats_data['latest']['min_latency'], 15.5, places=1)
        self.assertAlmostEqual(stats_data['latest']['max_latency'], 17.3, places=1)
        self.assertAlmostEqual(stats_data['latest']['avg_latency'], 16.533, places=1)
        
        # The same values should appear in the day_stats since there's only one record
        self.assertAlmostEqual(stats_data['day_stats']['min_latency'], 15.5, places=1)
        self.assertAlmostEqual(stats_data['day_stats']['max_latency'], 17.3, places=1)
        self.assertAlmostEqual(stats_data['day_stats']['avg_latency'], 16.533, places=1)
        # Max packet loss should equal the avg packet loss when there's only one record
        self.assertAlmostEqual(stats_data['day_stats']['max_packet_loss'], stats_data['day_stats']['avg_packet_loss'], places=1)

if __name__ == '__main__':
    unittest.main()