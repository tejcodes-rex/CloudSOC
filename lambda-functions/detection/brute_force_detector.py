import json
import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    detail = event.get('detail', {})
    
    if detail.get('errorCode') == 'Failure':
        source_ip = detail.get('sourceIPAddress', 'Unknown')
        username = detail.get('userIdentity', {}).get('userName', 'Unknown')
        
        message = {
            'AlarmName': 'Failed Console Login Detected',
            'Timestamp': detail.get('eventTime'),
            'Severity': 'HIGH',
            'SourceIP': source_ip,
            'Username': username,
            'EventID': detail.get('eventID'),
            'Recommendation': 'Investigate source IP and verify legitimate user activity'
        }
        
        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'
        
        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC] Failed Login Attempt',
            Message=json.dumps(message, indent=2)
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Detection complete')
    }
