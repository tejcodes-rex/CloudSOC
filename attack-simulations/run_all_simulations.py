"""
Master script to run all attack simulations in sequence.
This generates a comprehensive set of security events for testing CloudSOC.
"""

import time
import subprocess
import sys
import os

simulations = [
    ("Brute Force Attack", "simulate_brute_force.py"),
    ("Privilege Escalation", "simulate_privilege_escalation.py"),
    ("Root Account Usage", "simulate_root_usage.py"),
    ("Data Exfiltration", "simulate_data_exfiltration.py")
]

def run_simulation(name, script):
    """Run a single simulation script."""
    print(f"\n{'='*70}")
    print(f"RUNNING: {name}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            [sys.executable, script],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"\n[SUCCESS] {name} completed")
        else:
            print(f"\n[ERROR] {name} failed with exit code {result.returncode}")

    except Exception as e:
        print(f"\n[ERROR] Failed to run {name}: {e}")

    print(f"\nWaiting 5 seconds before next simulation...\n")
    time.sleep(5)

def main():
    print(f"\n{'#'*70}")
    print(f"# CloudSOC Attack Simulation Suite")
    print(f"# Running {len(simulations)} attack scenarios")
    print(f"{'#'*70}\n")

    print("[INFO] Ensure Elasticsearch is running at http://localhost:9200")
    print("[INFO] Ensure Docker containers are up: docker-compose ps\n")

    input("Press ENTER to start simulations or Ctrl+C to cancel...")

    start_time = time.time()

    for name, script in simulations:
        run_simulation(name, script)

    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"ALL SIMULATIONS COMPLETED")
    print(f"{'='*70}")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Total scenarios: {len(simulations)}")
    print(f"\nNext Steps:")
    print(f"1. Open Kibana: http://localhost:5601")
    print(f"2. Go to Discover and filter for today's events")
    print(f"3. Check Dashboard for severity distribution")
    print(f"4. Review Machine Learning anomalies (wait 15 minutes)")
    print(f"5. Verify alerts in your email (if SNS configured)")
    print(f"\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n[CANCELLED] Simulations interrupted by user")
        sys.exit(0)
