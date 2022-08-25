import boto3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

print("Creating resource...")
ec2_resource = boto3.resource(
        'ec2',
        region_name='us-east-1',
        aws_access_key_id=os.environ.get("aws_access_key"),
        aws_secret_access_key=os.environ.get("aws_secret_key")
    )

print("Creating client...")
ec2_client = boto3.client(
        'ec2',
        region_name='us-east-1',
        aws_access_key_id=os.environ.get("aws_access_key"),
        aws_secret_access_key=os.environ.get("aws_secret_key")
    )

print("Creating security group...")
sg = ec2_resource.create_security_group(
        GroupName="auth-redir-sg",
        Description="auth-redir-sg"
    )
ec2_client.authorize_security_group_ingress(
        GroupId=sg.id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 443,
             'ToPort': 443,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
	)

print("Creating key pair...")
kp = ec2_resource.create_key_pair(KeyName="auth-redir-key")
with open("keys/test", "w+") as f:
    f.write(kp.key_material)

print("Creating EC2 instance...")
instances = ec2_resource.create_instances(
        ImageId="ami-052efd3df9dad4825",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="auth-redir-key",
        SecurityGroupIds=[sg.id]
    )

print("Waiting until running...")
instances[0].wait_until_running()
running_ec2 = ec2_resource.Instance(instances[0].id)
print(running_ec2.public_ip_address)

input("Press enter to continue: ")
ec2_client.delete_key_pair(KeyName="auth-redir-key")
running_ec2.terminate()
running_ec2.wait_until_terminated()
ec2_client.delete_security_group(GroupId=sg.id)
