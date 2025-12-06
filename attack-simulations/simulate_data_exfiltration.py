"""
Simulates data exfiltration by generating suspicious S3 access patterns.
This demonstrates detection of unusual data download volumes.
"""

import requests
import json
from datetime import datetime
import time

ELASTICSEARCH_URL = "http://localhost:9200"

def simulate_data_exfiltration(bucket="sensitive-customer-data", count=10, attacker_ip="198.51.100.123"):
    """
    Generate multiple S3 GetObject events suggesting data theft.

    Args:
        bucket: Name of the sensitive S3 bucket
        count: Number of file downloads to simulate
        attacker_ip: Attacker's IP address
    """

    print(f"\n[DATA EXFILTRATION SIMULATION]")
    print(f"Simulating {count} suspicious downloads from {bucket}...")

    for i in range(count):
        event = {
            "@timestamp": datetime.utcnow().isoformat() + "Z",
            "eventVersion": "1.08",
            "eventTime": datetime.utcnow().isoformat() + "Z",
            "eventName": "GetObject",
            "eventSource": "s3.amazonaws.com",
            "awsRegion": "us-east-1",
            "sourceIPAddress": attacker_ip,
            "userAgent": "aws-cli/2.13.0 Python/3.11.0",
            "requestParameters": {
                "bucketName": bucket,
                "key": f"confidential/customer-data-{i:04d}.csv"
            },
            "responseElements": None,
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDAI23EXFIL999",
                "userName": "compromised-user",
                "arn": "arn:aws:iam::123456789012:user/compromised-user",
                "accountId": "123456789012",
                "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
            },
            "eventID": f"data-exfil-{i}-{int(time.time())}",
            "readOnly": True,
            "eventType": "AwsApiCall",
            "recipientAccountId": "123456789012",
            "resources": [
                {
                    "type": "AWS::S3::Object",
                    "ARN": f"arn:aws:s3:::{bucket}/confidential/customer-data-{i:04d}.csv"
                }
            ],
            "severity": "high",
            "threat_type": "data_exfiltration",
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
                print(f"  [{i+1}/{count}] S3 GetObject event sent - customer-data-{i:04d}.csv")
            else:
                print(f"  [{i+1}/{count}] Error: {response.status_code}")

        except Exception as e:
            print(f"  [{i+1}/{count}] Connection error: {e}")

        time.sleep(0.5)

    print(f"\n[COMPLETED] {count} suspicious S3 downloads generated")
    print(f"Expected Detection: High volume data access from {attacker_ip}")
    print(f"Expected Alert: Data exfiltration warning for manual review")
    print(f"Check: Kibana for spike in GetObject events from same user/IP")

if __name__ == "__main__":
    simulate_data_exfiltration(bucket="sensitive-customer-data", count=10)
