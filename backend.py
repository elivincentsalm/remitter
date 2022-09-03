import boto3
import json
import os
import uuid
from dotenv import load_dotenv, find_dotenv
from py2neo import Graph, Node, Relationship

load_dotenv(find_dotenv())

neo4j_uri = "bolt://neo4j:password@localhost:7687"
g = Graph(neo4j_uri)

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
        GroupName="http-redirector",
        Description="http-redirector"
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
kp_properties = vars(vars(kp)['meta'])['data']
if kp_properties["ResponseMetadata"]["HTTPStatusCode"]==200:
    del kp_properties["ResponseMetadata"]
else:
    print("Error. Key not created. Exiting...")
    exit()

tx = g.begin()
kp_node = Node("KeyPair", **kp_properties)
tx.create(kp_node)

group_name = 'http-redirector'
response = ec2_client.describe_security_groups(
        Filters=[dict(Name='group-name', Values=[group_name])]
    )
group_id = response['SecurityGroups'][0]['GroupId']

instances = ec2_resource.create_instances(
        ImageId="ami-052efd3df9dad4825",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="auth-redir-key",
        SecurityGroupIds=[group_id]
    )
instance_metadata = vars(vars(instances[0])['meta'])['data']
redirector_properties = {}
redirector_properties["InstanceId"] = instance_metadata["InstanceId"]
redirector_properties["KeyName"] = instance_metadata["KeyName"]
redirector_properties["AvailabilityZone"] = instance_metadata["Placement"]["AvailabilityZone"]
redirector_properties["PrivateIpAddress"] = instance_metadata["PrivateIpAddress"]
redirector_properties["State"] = instance_metadata["State"]["Name"]

redirector_node = Node("Redirector", **redirector_properties)
ki = Relationship(kp_node, "BELONGS_TO", redirector_node)

tx.create(redirector_node)
tx.create(ki)

print("Waiting until running...")
instances[0].wait_until_running()
running_ec2 = ec2_resource.Instance(instances[0].id)
g.commit(tx)
print(running_ec2.public_ip_address)

input("Press enter to continue: ")
g.run("MATCH (n) DETACH DELETE n;")
ec2_client.delete_key_pair(KeyName="auth-redir-key")
running_ec2.terminate()
running_ec2.wait_until_terminated()
ec2_client.delete_security_group(GroupId=sg.id)
