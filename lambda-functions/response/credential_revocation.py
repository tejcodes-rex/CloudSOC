import json
import boto3

iam = boto3.client('iam')
sns = boto3.client('sns')

def lambda_handler(event, context):
    """
    Revokes all access keys for a compromised IAM user.
    This prevents the user from making API calls but doesn't affect console access.
    """

    username = event.get('username')
    reason = event.get('reason', 'Security violation detected')

    if not username:
        return {
            'statusCode': 400,
            'body': json.dumps('username is required')
        }

    try:
        keys_response = iam.list_access_keys(UserName=username)

        disabled_keys = []

        for key in keys_response['AccessKeyMetadata']:
            access_key_id = key['AccessKeyId']

            if key['Status'] == 'Active':
                iam.update_access_key(
                    UserName=username,
                    AccessKeyId=access_key_id,
                    Status='Inactive'
                )

                disabled_keys.append({
                    'AccessKeyId': access_key_id,
                    'CreateDate': str(key['CreateDate']),
                    'PreviousStatus': 'Active',
                    'NewStatus': 'Inactive'
                })

        message = {
            'Action': 'Credentials Revoked',
            'User': username,
            'Reason': reason,
            'KeysDisabled': len(disabled_keys),
            'Keys': disabled_keys,
            'Status': 'SUCCESS',
            'Impact': 'User cannot make API calls. Console access still active.',
            'NextSteps': [
                'Review user activity in CloudTrail',
                'Determine if account should be deleted',
                'Force password reset if console access compromised',
                'Enable MFA if not already enabled'
            ]
        }

        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC RESPONSE] Credentials Revoked',
            Message=json.dumps(message, indent=2)
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'revoked',
                'user': username,
                'keys_disabled': len(disabled_keys)
            })
        }

    except iam.exceptions.NoSuchEntityException:
        error_message = {
            'Action': 'Credential Revocation FAILED',
            'User': username,
            'Error': 'User not found',
            'Status': 'FAILED'
        }

        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC ERROR] Credential Revocation Failed',
            Message=json.dumps(error_message, indent=2)
        )

        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'User not found'})
        }

    except Exception as e:
        error_message = {
            'Action': 'Credential Revocation FAILED',
            'User': username,
            'Error': str(e),
            'Status': 'FAILED'
        }

        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC ERROR] Credential Revocation Failed',
            Message=json.dumps(error_message, indent=2)
        )

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
