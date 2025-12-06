import json
import boto3
from datetime import datetime, timedelta

sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    detail = event.get('detail', {})
    event_name = detail.get('eventName')

    if event_name in ['GetObject', 'ListBucket']:
        bucket_name = detail.get('requestParameters', {}).get('bucketName', 'Unknown')
        user = detail.get('userIdentity', {}).get('userName', 'Unknown')
        source_ip = detail.get('sourceIPAddress', 'Unknown')

        if bucket_name.startswith('sensitive-') or bucket_name.startswith('secret-'):

            message = {
                'AlarmName': 'Potential Data Exfiltration Detected',
                'Timestamp': detail.get('eventTime'),
                'Severity': 'HIGH',
                'User': user,
                'Bucket': bucket_name,
                'Action': event_name,
                'SourceIP': source_ip,
                'EventID': detail.get('eventID'),
                'Recommendation': 'Review S3 access patterns and verify legitimate data access',
                'ManualAction': 'Check CloudTrail for volume of downloads from this user'
            }

            topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

            sns.publish(
                TopicArn=topic_arn,
                Subject='[CloudSOC] Potential Data Exfiltration',
                Message=json.dumps(message, indent=2)
            )

    return {
        'statusCode': 200,
        'body': json.dumps('Data exfiltration check complete')
    }
