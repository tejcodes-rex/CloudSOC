"""
Simulates root account usage which should ALWAYS trigger an alert.
Root account usage is a critical security concern.
"""

import requests
import json
from datetime import datetime
import time

ELASTICSEARCH_URL = "http://localhost:9200"

def simulate_root_usage(action="DescribeInstances", source_ip="192.0.2.100"):
    """
    Generate root account activity event.

    Args:
        action: AWS API action performed by root
        source_ip: Source IP address
    """

    print(f"\n[ROOT ACCOUNT USAGE SIMULATION]")
    print(f"Simulating root account performing {action}...")

    event = {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "eventVersion": "1.08",
        "eventTime": datetime.utcnow().isoformat() + "Z",
        "eventName": action,
        "eventSource": "ec2.amazonaws.com",
        "awsRegion": "us-east-1",
        "sourceIPAddress": source_ip,
        "userAgent": "console.aws.amazon.com",
        "requestParameters": {
            "instancesSet": {},
            "filterSet": {}
        },
        "responseElements": None,
        "userIdentity": {
            "type": "Root",
            "principalId": "123456789012",
            "arn": "arn:aws:iam::123456789012:root",
            "accountId": "123456789012",
            "accessKeyId": None
        },
        "eventID": f"root-usage-{int(time.time())}",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "recipientAccountId": "123456789012",
        "severity": "critical",
        "threat_type": "root_usage",
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
            print(f"  [SUCCESS] Root account usage event sent")
            print(f"  Action: {action}")
            print(f"  Source IP: {source_ip}")
            print(f"  User Type: Root (CRITICAL)")
        else:
            print(f"  [ERROR] {response.status_code} - {response.text}")

    except Exception as e:
        print(f"  [CONNECTION ERROR] {e}")

    print(f"\n[COMPLETED] Root account usage simulation complete")
    print(f"Expected Detection: CRITICAL alert - root account should NEVER be used")
    print(f"Recommendation: Investigate immediately, verify MFA enabled on root")

if __name__ == "__main__":
    simulate_root_usage(action="DescribeInstances")
