import json
import boto3

sns = boto3.client('sns')
iam = boto3.client('iam')

def lambda_handler(event, context):
    detail = event.get('detail', {})
    event_name = detail.get('eventName')
    
    if event_name in ['AttachUserPolicy', 'AttachRolePolicy', 'AttachGroupPolicy']:
        policy_arn = detail.get('requestParameters', {}).get('policyArn', '')
        user_name = detail.get('requestParameters', {}).get('userName', 'Unknown')
        
        dangerous_policies = [
            'arn:aws:iam::aws:policy/AdministratorAccess',
            'arn:aws:iam::aws:policy/PowerUserAccess',
            'arn:aws:iam::aws:policy/IAMFullAccess'
        ]
        
        if policy_arn in dangerous_policies:
            message = {
                'AlarmName': 'Privilege Escalation Detected',
                'Timestamp': detail.get('eventTime'),
                'Severity': 'CRITICAL',
                'User': user_name,
                'Action': event_name,
                'PolicyArn': policy_arn,
                'SourceIP': detail.get('sourceIPAddress'),
                'Response': 'Credentials should be revoked',
                'ManualAction': 'Investigate user account immediately'
            }
            
            topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'
            
            sns.publish(
                TopicArn=topic_arn,
                Subject='[CloudSOC CRITICAL] Privilege Escalation Detected',
                Message=json.dumps(message, indent=2)
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Privilege escalation check complete')
    }
