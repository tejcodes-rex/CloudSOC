"""
Simulates a privilege escalation attack by generating IAM policy attachment events.
This demonstrates detection of administrative privilege assignments.
"""

import requests
import json
from datetime import datetime
import time

ELASTICSEARCH_URL = "http://localhost:9200"

def simulate_privilege_escalation(target_user="compromised-user", attacker_ip="198.51.100.42"):
    """
    Generate privilege escalation event (attaching AdministratorAccess policy).

    Args:
        target_user: The IAM user receiving elevated privileges
        attacker_ip: Source IP of the attacker
    """

    print(f"\n[PRIVILEGE ESCALATION SIMULATION]")
    print(f"Simulating AdministratorAccess policy attachment to {target_user}...")

    event = {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "eventVersion": "1.08",
        "eventTime": datetime.utcnow().isoformat() + "Z",
        "eventName": "AttachUserPolicy",
        "eventSource": "iam.amazonaws.com",
        "awsRegion": "us-east-1",
        "sourceIPAddress": attacker_ip,
        "userAgent": "aws-cli/2.13.0",
        "requestParameters": {
            "userName": target_user,
            "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        "responseElements": None,
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAI23ATTACKER999",
            "userName": "attacker",
            "arn": "arn:aws:iam::123456789012:user/attacker",
            "accountId": "123456789012",
            "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
        },
        "eventID": f"privilege-escalation-{int(time.time())}",
        "readOnly": False,
        "eventType": "AwsApiCall",
        "recipientAccountId": "123456789012",
        "severity": "critical",
        "threat_type": "privilege_escalation",
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
            print(f"  [SUCCESS] Privilege escalation event sent")
            print(f"  User: {target_user}")
            print(f"  Policy: AdministratorAccess")
            print(f"  Attacker IP: {attacker_ip}")
        else:
            print(f"  [ERROR] {response.status_code} - {response.text}")

    except Exception as e:
        print(f"  [CONNECTION ERROR] {e}")

    print(f"\n[COMPLETED] Privilege escalation simulation complete")
    print(f"Expected Detection: CRITICAL severity alert in Kibana")
    print(f"Expected Response: Credential revocation recommended")

if __name__ == "__main__":
    simulate_privilege_escalation(target_user="compromised-user")
