"""
Simulates a brute force attack by generating failed login events.
This script sends test events to Elasticsearch to demonstrate detection capabilities.
"""

import requests
import json
from datetime import datetime
import time

ELASTICSEARCH_URL = "http://localhost:9200"

def simulate_failed_logins(count=6, attacker_ip="203.0.113.42"):
    """
    Generate multiple failed login attempts from the same IP address.

    Args:
        count: Number of failed login attempts to generate
        attacker_ip: Source IP address of the attacker
    """

    print(f"\n[BRUTE FORCE SIMULATION]")
    print(f"Generating {count} failed login attempts from {attacker_ip}...")

    for i in range(count):
        event = {
            "@timestamp": datetime.utcnow().isoformat() + "Z",
            "eventVersion": "1.08",
            "eventTime": datetime.utcnow().isoformat() + "Z",
            "eventName": "ConsoleLogin",
            "eventSource": "signin.amazonaws.com",
            "awsRegion": "us-east-1",
            "sourceIPAddress": attacker_ip,
            "userAgent": "Mozilla/5.0",
            "errorCode": "Failure",
            "errorMessage": "Failed authentication",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDAI23SKGJE8EXAMPLE",
                "userName": "admin",
                "arn": "arn:aws:iam::123456789012:user/admin",
                "accountId": "123456789012"
            },
            "eventID": f"brute-force-test-{i}-{int(time.time())}",
            "readOnly": False,
            "eventType": "AwsConsoleSignIn",
            "recipientAccountId": "123456789012",
            "responseElements": {
                "ConsoleLogin": "Failure"
            },
            "severity": "high",
            "threat_type": "brute_force",
            "log_type": "cloudtrail"
        }

        index = f"cloudsoc-logs-{datetime.utcnow().strftime('%Y.%m.%d')}"

        try:
            response = requests.post(
                f"{ELASTICSEARCH_URL}/{index}/_doc",
                json=event,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                print(f"  [{i+1}/{count}] Failed login event sent successfully")
            else:
                print(f"  [{i+1}/{count}] Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  [{i+1}/{count}] Connection error: {e}")

        time.sleep(1)

    print(f"\n[COMPLETED] {count} failed login events generated")
    print(f"Expected Detection: Brute force alert in Kibana ML or EventBridge")
    print(f"Check: Kibana Dashboard for high-severity events from {attacker_ip}")

if __name__ == "__main__":
    simulate_failed_logins(count=6, attacker_ip="203.0.113.42")
