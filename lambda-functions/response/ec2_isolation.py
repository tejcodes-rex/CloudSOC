import json
import boto3

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    """
    Isolates a compromised EC2 instance by replacing its security groups
    with an isolation security group that has no ingress rules.
    """

    instance_id = event.get('instance_id')
    reason = event.get('reason', 'Security threat detected')

    if not instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps('instance_id is required')
        }

    try:
        isolation_sg_name = f'isolation-{instance_id}'

        try:
            describe_sg = ec2.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [isolation_sg_name]}]
            )

            if describe_sg['SecurityGroups']:
                isolation_sg_id = describe_sg['SecurityGroups'][0]['GroupId']
            else:
                raise Exception('SG not found')

        except:
            vpc_response = ec2.describe_instances(InstanceIds=[instance_id])
            vpc_id = vpc_response['Reservations'][0]['Instances'][0]['VpcId']

            create_sg = ec2.create_security_group(
                GroupName=isolation_sg_name,
                Description=f'Isolation security group for {instance_id} - NO INGRESS ALLOWED',
                VpcId=vpc_id
            )
            isolation_sg_id = create_sg['GroupId']

        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[isolation_sg_id]
        )

        message = {
            'Action': 'EC2 Instance Isolated',
            'InstanceId': instance_id,
            'SecurityGroup': isolation_sg_id,
            'Reason': reason,
            'Status': 'SUCCESS',
            'Impact': 'All network ingress blocked. Egress still allowed.',
            'NextSteps': 'Investigate the instance, review logs, determine if termination needed'
        }

        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC RESPONSE] EC2 Instance Isolated',
            Message=json.dumps(message, indent=2)
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'isolated',
                'instance': instance_id,
                'security_group': isolation_sg_id
            })
        }

    except Exception as e:
        error_message = {
            'Action': 'EC2 Isolation FAILED',
            'InstanceId': instance_id,
            'Error': str(e),
            'Status': 'FAILED'
        }

        topic_arn = 'arn:aws:sns:us-east-1:123456789012:cloudsoc-security-alerts'

        sns.publish(
            TopicArn=topic_arn,
            Subject='[CloudSOC ERROR] EC2 Isolation Failed',
            Message=json.dumps(error_message, indent=2)
        )

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
