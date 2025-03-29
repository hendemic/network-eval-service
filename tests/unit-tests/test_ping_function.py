import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the main project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.pingTest import ping_test


class TestPingFunction(unittest.TestCase):
    @patch('backend.pingTest.subprocess.Popen')
    def test_successful_ping(self, mock_popen):
        # Setup mock
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Sample output that would come from a successful ping
        mock_process.stdout.readline.side_effect = [
            "PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.",
            "64 bytes from 1.1.1.1: icmp_seq=1 ttl=55 time=12.3 ms",
            "64 bytes from 1.1.1.1: icmp_seq=2 ttl=55 time=14.5 ms",
            "64 bytes from 1.1.1.1: icmp_seq=3 ttl=55 time=13.2 ms",
            "\n",  # Empty line to signal end of output
            ""
        ]
        
        # Call the function being tested
        result = ping_test(target="1.1.1.1", count=3, interval="0.1")
        
        # Check the results
        self.assertEqual(result["target"], "1.1.1.1")
        self.assertEqual(result["packets_sent"], 3)
        self.assertEqual(result["packets_received"], 3)
        self.assertEqual(result["packet_loss"], 0.0)
        self.assertEqual(result["min_latency"], 12.3)
        self.assertEqual(result["max_latency"], 14.5)
        self.assertEqual(result["avg_latency"], (12.3 + 14.5 + 13.2) / 3)
        self.assertAlmostEqual(result["jitter"], (abs(14.5 - 12.3) + abs(13.2 - 14.5)) / 2, places=1)
        
    @patch('backend.pingTest.subprocess.Popen')
    def test_packet_loss(self, mock_popen):
        # Setup mock with packet loss
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Sample output with packet loss
        mock_process.stdout.readline.side_effect = [
            "PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.",
            "64 bytes from 1.1.1.1: icmp_seq=1 ttl=55 time=10.1 ms",
            "From 192.168.1.1 icmp_seq=2 Destination Host Unreachable",  # Lost packet
            "64 bytes from 1.1.1.1: icmp_seq=3 ttl=55 time=11.3 ms",
            "From 192.168.1.1 icmp_seq=4 Destination Host Unreachable",  # Lost packet
            "64 bytes from 1.1.1.1: icmp_seq=5 ttl=55 time=9.8 ms",
            ""
        ]
        
        # Call the function
        result = ping_test(target="1.1.1.1", count=5, interval="0.1")
        
        # Verify results
        self.assertEqual(result["packets_sent"], 5)
        self.assertEqual(result["packets_received"], 3)
        self.assertEqual(result["packet_loss"], 40.0)  # 2 out of 5 lost = 40%
        self.assertEqual(result["min_latency"], 9.8)
        self.assertEqual(result["max_latency"], 11.3)
        self.assertEqual(result["avg_latency"], (10.1 + 11.3 + 9.8) / 3)
        
    @patch('backend.pingTest.subprocess.Popen')
    def test_all_packets_lost(self, mock_popen):
        # Setup mock with all packets lost
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # All packets timeout
        mock_process.stdout.readline.side_effect = [
            "PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.",
            "From 192.168.1.1 icmp_seq=1 Destination Host Unreachable",
            "From 192.168.1.1 icmp_seq=2 Destination Host Unreachable",
            "From 192.168.1.1 icmp_seq=3 Destination Host Unreachable",
            ""
        ]
        
        # Call the function
        result = ping_test(target="1.1.1.1", count=3, interval="0.1")
        
        # Verify results
        self.assertEqual(result["packets_sent"], 3)
        self.assertEqual(result["packets_received"], 0)
        self.assertEqual(result["packet_loss"], 100.0)  # All packets lost
        self.assertEqual(result["min_latency"], 0)
        self.assertEqual(result["max_latency"], 0)
        self.assertEqual(result["avg_latency"], 0)
        self.assertEqual(result["jitter"], 0)
        
    @patch('backend.pingTest.subprocess.Popen', side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt(self, mock_popen):
        # Test what happens when the user interrupts the test
        result = ping_test()
        
        # Should return an empty dictionary on interrupt
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
