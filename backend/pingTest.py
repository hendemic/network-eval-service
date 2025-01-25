import subprocess
import platform
import re

def ping_test():
    target = "1.1.1.1"
    count = 100
    interval = "0.1"  # Seconds (decimal values supported)

    # Send pings
    command = ["ping", "-c", str(count), "-i", interval, "-W", "1", target]

    latencies = []
    lost_packets = 0

    # Run ping command and parse output
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            # Check for packet loss indicators
            if "timeout" in line.lower() or "unreachable" in line.lower():
                lost_packets += 1
            # Parse successful ping responses
            match = re.search(r"time=([\d.]+)\s*ms", line)
            if match:
                latencies.append(float(match.group(1)))
    except KeyboardInterrupt:
        print("\nTest aborted by user")
        return

    # Calculate statistics
    total_packets = count
    received_packets = len(latencies)
    lost_packets = total_packets - received_packets
    packet_loss = (lost_packets / total_packets) * 100 if total_packets > 0 else 0

    if received_packets > 0:
        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = sum(latencies) / received_packets

        # Calculate jitter (average of absolute differences between consecutive packets)
        jitter = 0
        if len(latencies) > 1:
            differences = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
            jitter = sum(differences) / len(differences)
    else:
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

if __name__ == "__main__":
    ping_test()
