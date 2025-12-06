import requests
import json
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ELASTICSEARCH_URL = "http://localhost:9200"

def send_event(event):
    index = f"cloudsoc-logs-{datetime.utcnow().strftime('%Y.%m.%d')}"
    try:
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{index}/_doc",
            json=event,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

print("="*70)
print(" " * 20 + "CloudSOC - Test Detection System")
print("="*70)
print("\n\033[93m[INFO]\033[0m This script sends test CloudTrail events to verify detection")
print("\033[93m[INFO]\033[0m Events will appear in Kibana dashboard at http://localhost:5601\n")

events = [
    {
        "name": "Brute Force Attack (Failed Login)",
        "event": {
            "@timestamp": datetime.utcnow().isoformat(),
            "eventName": "ConsoleLogin",
            "eventSource": "signin.amazonaws.com",
            "errorCode": "Failure",
            "sourceIPAddress": "203.0.113.42",
            "userIdentity": {
                "type": "IAMUser",
                "userName": "test-user"
            },
            "severity": "high",
            "threat_type": "brute_force"
        }
    },
    {
        "name": "Privilege Escalation (IAM Policy Change)",
        "event": {
            "@timestamp": datetime.utcnow().isoformat(),
            "eventName": "AttachUserPolicy",
            "eventSource": "iam.amazonaws.com",
            "requestParameters": {
                "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                "userName": "test-user"
            },
            "sourceIPAddress": "203.0.113.42",
            "severity": "critical",
            "threat_type": "privilege_escalation"
        }
    },
    {
        "name": "Root Account Usage",
        "event": {
            "@timestamp": datetime.utcnow().isoformat(),
            "eventName": "DescribeInstances",
            "eventSource": "ec2.amazonaws.com",
            "userIdentity": {
                "type": "Root"
            },
            "sourceIPAddress": "203.0.113.42",
            "severity": "critical",
            "threat_type": "root_usage"
        }
    },
    {
        "name": "Security Group Change (SSH from 0.0.0.0/0)",
        "event": {
            "@timestamp": datetime.utcnow().isoformat(),
            "eventName": "AuthorizeSecurityGroupIngress",
            "eventSource": "ec2.amazonaws.com",
            "requestParameters": {
                "ipPermissions": {
                    "fromPort": 22,
                    "toPort": 22,
                    "ipRanges": ["0.0.0.0/0"]
                }
            },
            "sourceIPAddress": "203.0.113.42",
            "severity": "high",
            "threat_type": "security_group"
        }
    }
]

results = []
for item in events:
    print(f"\033[93mTesting:\033[0m {item['name']}")
    if send_event(item['event']):
        print(f"\033[92m[OK]\033[0m Test event sent: {item['event']['threat_type']}\n")
        results.append("OK")
    else:
        print(f"\033[91m[FAIL]\033[0m Failed to send: {item['name']}\n")
        results.append("FAIL")

print("="*70)
print(" " * 25 + "Test Results")
print("="*70 + "\n")

for i, item in enumerate(events):
    status = results[i]
    color = "\033[92m" if status == "OK" else "\033[91m"
    print(f"{color}[{status}]\033[0m {item['name']}: {status}")

print(f"\n\033[94mResult: {results.count('OK')}/{len(results)} tests passed\033[0m\n")

if results.count('OK') == len(results):
    print("\033[92m[OK]\033[0m All test events sent successfully!")
else:
    print("\033[91m[FAIL]\033[0m Some tests failed. Check Elasticsearch connection.")

print("\033[93m[INFO]\033[0m \nNext steps:")
print("\033[93m[INFO]\033[0m 1. Open Kibana: http://localhost:5601")
print("\033[93m[INFO]\033[0m 2. Go to 'Discover' tab")
print("\033[93m[INFO]\033[0m 3. Search for: log_type:cloudtrail")
print("\033[93m[INFO]\033[0m 4. You should see the test events\n")
print("="*70)
