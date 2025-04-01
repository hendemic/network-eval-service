import subprocess
import re
import datetime
from typing import Dict, List, Optional, Union, Tuple

def ping_test(target: str = "1.1.1.1", count: int = 100, interval: str = "0.1") -> Dict[str, Union[float, str, datetime.datetime]]:
    """Run a network ping test to measure connectivity and performance metrics.
    
    This function performs a network ping test by executing the system's ping 
    command and parsing the results to extract latency, jitter, and packet loss data.
    This provides the core measurement functionality for the entire application.
    
    Args:
        target: The IP address or hostname to test (default: Cloudflare DNS at 1.1.1.1)
        count: Number of ping packets to send (higher values = more accurate results)
        interval: Time between pings in seconds (smaller = more intensive test)
        
    Returns:
        Dictionary containing all network performance metrics:
        - timestamp: UTC timestamp when the test was conducted
        - target: The tested host
        - packet_loss: Percentage of packets lost (0-100)
        - min_latency: Minimum round-trip time in milliseconds
        - max_latency: Maximum round-trip time in milliseconds
        - avg_latency: Average round-trip time in milliseconds
        - jitter: Variation in latency (calculated from consecutive packets)
        - packets_sent: Total packets transmitted
        - packets_received: Total packets successfully received
    """
    # Construct ping command with appropriate parameters
    # -c: count of pings to send
    # -i: interval between pings
    # -W: timeout for each ping in seconds 
    command = ["ping", "-c", str(count), "-i", interval, "-W", "1", target]

    # Initialize data collection variables
    latencies = []  # Store all successful ping times
    lost_packets = 0  # Count packets that timed out or failed

    # Run ping command and parse output line by line in real-time
    try:
        # Start process with pipe to capture output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
        
        # Process each line of output as it comes in
        while True:
            line = process.stdout.readline()
            if not line:  # End of output
                break
                
            # Detect packet loss by looking for error messages in the output
            if "timeout" in line.lower() or "unreachable" in line.lower():
                lost_packets += 1
                
            # Parse successful ping responses by extracting the time value
            # The regex looks for patterns like "time=23.4 ms"
            match = re.search(r"time=([\d.]+)\s*ms", line)
            if match:
                # Convert the matched time value to float and store it
                latencies.append(float(match.group(1)))
    except KeyboardInterrupt:
        # Handle user interruption gracefully
        print("\nTest aborted by user")
        return {}

    # Calculate performance statistics from collected data
    total_packets = count  # The total number of pings we sent
    received_packets = len(latencies)  # Count of successful pings
    
    # Update lost_packets based on the actual difference
    # (More accurate than counting "timeout" messages)
    lost_packets = total_packets - received_packets
    
    # Calculate packet loss percentage (0-100%)
    packet_loss = (lost_packets / total_packets) * 100 if total_packets > 0 else 0

    # Only calculate latency statistics if we received any packets
    if received_packets > 0:
        # Basic latency statistics
        min_latency = min(latencies)  # Minimum round-trip time
        max_latency = max(latencies)  # Maximum round-trip time
        avg_latency = sum(latencies) / received_packets  # Average round-trip time

        # Calculate jitter (network stability metric)
        # Jitter is the average deviation between consecutive packets
        jitter = 0
        if len(latencies) > 1:
            # Calculate average of absolute differences between consecutive packets
            # Higher jitter = less stable connection
            jitter = sum(abs(latencies[i] - latencies[i-1]) 
                         for i in range(1, len(latencies))) / (len(latencies) - 1)
    else:
        # No packets received, set all metrics to zero
        min_latency = max_latency = avg_latency = jitter = 0

    # Print results
    print(f"\n--- Ping statistics for {target} ---")
    print(f"Packet loss: {packet_loss:.2f}%")
    if received_packets > 0:
        print(f"Latency (ms):")
        print(f"    Minimum = {min_latency:.2f}ms")
        print(f"    Maximum = {max_latency:.2f}ms")
        print(f"    Average = {avg_latency:.2f}ms")
        print(f"Jitter = {jitter:.2f}ms")
    else:
        print("No packets received")
    
    # Return results as dictionary for database storage and API responses
    return {
        # Always use UTC time for consistency across timezones and servers
        "timestamp": datetime.datetime.utcnow(),
        
        # Test configuration
        "target": target,
        
        # Core network metrics (all standardized for database storage)
        "packet_loss": packet_loss,      # percentage (0-100)
        "min_latency": min_latency,      # milliseconds
        "max_latency": max_latency,      # milliseconds
        "avg_latency": avg_latency,      # milliseconds
        "jitter": jitter,                # milliseconds
        
        # Additional test details
        "packets_sent": total_packets,
        "packets_received": received_packets
    }

if __name__ == "__main__":
    ping_test()
