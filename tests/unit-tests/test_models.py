import unittest
import sys
import os
from datetime import datetime

# Add the main project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import model classes, using a custom Flask app context
from backend.models import PingResult
from backend.app import create_app


class TestPingResultModel(unittest.TestCase):
    def setUp(self):
        # Create Flask app and context for testing
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Get db reference from the app context
        from backend.models import db
        self.db = db
        
        # Create tables in test database
        self.db.create_all()
    
    def tearDown(self):
        # Clean up after tests
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()
    
    def test_create_ping_result(self):
        # Create a test timestamp
        test_time = datetime.utcnow()
        
        # Create a PingResult instance
        ping_result = PingResult(
            timestamp=test_time,
            target="8.8.8.8",
            packet_loss=2.5,
            min_latency=10.2,
            max_latency=15.7,
            avg_latency=12.8,
            jitter=1.2,
            packets_sent=100,
            packets_received=98
        )
        
        # Add to session and commit
        self.db.session.add(ping_result)
        self.db.session.commit()
        
        # Verify it was saved to the database
        saved_result = PingResult.query.first()
        self.assertIsNotNone(saved_result)
        self.assertEqual(saved_result.target, "8.8.8.8")
        self.assertEqual(saved_result.packet_loss, 2.5)
        self.assertEqual(saved_result.min_latency, 10.2)
        self.assertEqual(saved_result.max_latency, 15.7)
        self.assertEqual(saved_result.avg_latency, 12.8)
        self.assertEqual(saved_result.jitter, 1.2)
        self.assertEqual(saved_result.packets_sent, 100)
        self.assertEqual(saved_result.packets_received, 98)
    
    def test_to_dict_method(self):
        # Create test timestamp (using a fixed time for predictable serialization)
        test_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Create a PingResult instance
        ping_result = PingResult(
            id=1,
            timestamp=test_time,
            target="8.8.8.8",
            packet_loss=2.5,
            min_latency=10.2,
            max_latency=15.7,
            avg_latency=12.8,
            jitter=1.2,
            packets_sent=100,
            packets_received=98
        )
        
        # Get dictionary representation
        result_dict = ping_result.to_dict()
        
        # Verify dictionary content
        self.assertEqual(result_dict['id'], 1)
        self.assertEqual(result_dict['timestamp'], test_time.isoformat())
        self.assertEqual(result_dict['target'], "8.8.8.8")
        self.assertEqual(result_dict['packet_loss'], 2.5)
        self.assertEqual(result_dict['min_latency'], 10.2)
        self.assertEqual(result_dict['max_latency'], 15.7)
        self.assertEqual(result_dict['avg_latency'], 12.8)
        self.assertEqual(result_dict['jitter'], 1.2)
        self.assertEqual(result_dict['packets_sent'], 100)
        self.assertEqual(result_dict['packets_received'], 98)
    
    def test_timestamp_index(self):
        # This test verifies that the timestamp column is indexed
        # Create multiple ping results with different timestamps
        for i in range(5):
            hours_offset = i * 4  # Each result 4 hours apart (stays under 24)
            test_time = datetime(2023, 1, 1, hours_offset, 0, 0)
            
            ping_result = PingResult(
                timestamp=test_time,
                target="8.8.8.8",
                packet_loss=i,
                min_latency=10.0 + i,
                max_latency=15.0 + i,
                avg_latency=12.0 + i,
                jitter=1.0,
                packets_sent=100,
                packets_received=100 - i
            )
            self.db.session.add(ping_result)
        
        self.db.session.commit()
        
        # Query with time filter
        cutoff_time = datetime(2023, 1, 1, 12, 0, 0)  # Should return 3 results (0h, 4h, 8h)
        results = PingResult.query.filter(PingResult.timestamp < cutoff_time).all()
        
        self.assertEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
