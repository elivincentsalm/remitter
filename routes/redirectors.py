import boto3
import io
import json
import os
import paramiko
import redis
import scp
import subprocess
import time
import uuid
from dotenv import load_dotenv, find_dotenv
from flask import Blueprint, request, abort
from rq import Connection, Queue 
from rq.job import Job
from py2neo import Graph, Node, Relationship


load_dotenv(find_dotenv())

neo4j_uri = "bolt://neo4j:password@localhost:7687"
g = Graph(neo4j_uri)

ec2_resource = boto3.resource(
    'ec2',
    region_name='us-east-1',
    aws_access_key_id=os.environ.get("aws_access_key"),
    aws_secret_access_key=os.environ.get("aws_secret_key")
)

ec2_client = boto3.client(
	'ec2',
	region_name='us-east-1',
	aws_access_key_id=os.environ.get("aws_access_key"),
	aws_secret_access_key=os.environ.get("aws_secret_key")
)

redirectors = Blueprint(name="redirectors", import_name=__name__)

redis_url = "redis://localhost:6379"
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

'''
GET - Get all redirectors
POST - Create redirector
DELETE - Delete all redirectors
'''
@redirectors.route("/", methods=['GET', 'POST', 'DELETE'], defaults={'redirector_id': None})
@redirectors.route("/<redirector_id>", methods=['GET', 'DELETE'])
def redirectors_handler(redirector_id):
    if redirector_id==None:
        if request.method=="GET":
            instances = g.run('MATCH (r:Redirector) RETURN DISTINCT r;').data()
            return instances
        elif request.method=="POST":
            job = q.enqueue_call(func=create_aws_redirector)
            status = {"status": "error"}
            return status
        elif request.method=="DELETE":
            job = q.enqueue_call(func=delete_aws_redirectors)
            status = {"status": "success"}
            return status
    else:
        if redirector_id=="test":
            abort(404)
        instance = ec2_resouce.Instance(redirector_id)
        if request.method=="GET":
            return serialize(instance)
        elif request.method=="DELETE":
            instance.terminate()
            return job.get_id()

'''
GET - Get specific redirector
DELETE - Delete specific redirector
'''
def serialize(i):
    return vars(vars(i)['meta'])['data']


# for AWS below, not sure how exactly I will structure this logic
def create_aws_redirector():
    tx = g.begin()
    sg_uuid = str(uuid.uuid4())
    sg = ec2_resource.create_security_group(GroupName=sg_uuid, Description=sg_uuid)
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
    response = ec2_client.describe_security_groups(
            Filters=[dict(Name='group-name', Values=[sg_uuid])]
        )
    group_id = response['SecurityGroups'][0]['GroupId']
    
    fwrule_properties = {"Name": sg_uuid, "RuleId": str(uuid.uuid4()), "NativeRuleId": group_id}
    fwrule_node = Node("FirewallRuleset", **fwrule_properties )

    # Create KeyPair
    kp_uuid = str(uuid.uuid4())
    kp = ec2_resource.create_key_pair(KeyName=kp_uuid)
    kp_metadata = serialize(kp)
    if kp_metadata["ResponseMetadata"]["HTTPStatusCode"]!=200:
        raise Exception("Failed to create AWS KeyPair.")

    # Add KeyPair to DB
    del kp_metadata["ResponseMetadata"]
    kp_metadata["KeyPairType"] = "ssh"
    kp_node = Node("KeyPair", **kp_metadata)
    tx.create(kp_node)

    # create ec2 instance
    instances = ec2_resource.create_instances(
        ImageId="ami-052efd3df9dad4825",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName=kp_uuid,
        SecurityGroupIds=[group_id]
    )
    # add instance to DB
        # add key pair to instance
        # add SG to instance
    instance_metadata = serialize(instances[0])
    redirector_properties = {
        "InstanceId": instance_metadata["InstanceId"],
        "KeyName": instance_metadata["KeyName"],
        "AvailabilityZone": instance_metadata["Placement"]["AvailabilityZone"],
        "PrivateIpAddress": instance_metadata["PrivateIpAddress"],
        "State": instance_metadata["State"]["Name"]
    }
    redirector_node = Node("Redirector", **redirector_properties)
    ki = Relationship(kp_node, "BELONGS_TO", redirector_node)
    fi = Relationship(fwrule_node, "APPLIES_TO", redirector_node)
    tx.create(redirector_node)
    tx.create(ki)
    tx.create(fi)
    g.commit(tx)

    instances[0].wait_until_running()
    i = ec2_resource.Instance(redirector_properties["InstanceId"])
    # should put this in a different function, along with the DB queries, because across CSPs this will repeat code
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pk = paramiko.RSAKey.from_private_key(io.StringIO(kp_metadata['KeyMaterial']))
    time.sleep(30)
    client.connect(i.public_ip_address, username='ubuntu', pkey=pk)
    scp_client = scp.SCPClient(client.get_transport())
    with open("routes/redirectors/nginx_setup.sh", "r+") as f:
        for cmd in f.readlines():
            if cmd[:3]=="SCP":
                _, src, dest = cmd.split()
                scp_client.put(src, dest, recursive=True)
            else:
                stdin, stdout, stderr = client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                if exit_status!=0:
                    print("ERROR: remote command failed")
                    print(cmd)


def delete_aws_redirectors():
    data = g.run('MATCH (r:Redirector) RETURN DISTINCT r;').data()
    for r in data:
        instance_id = r["r"]["InstanceId"]
        ssh_key = g.run('MATCH (kp:KeyPair)-[]->(r:Redirector {InstanceId: "' + instance_id + '"}) RETURN kp;').data()[0]["kp"]
        sg = g.run('MATCH (sg:FirewallRuleset)-[]->(r:Redirector {InstanceId: "' + instance_id + '"}) RETURN sg;').data()[0]["sg"]
        instance = ec2_resource.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
        ec2_client.delete_key_pair(KeyName=ssh_key["KeyName"])
        ec2_client.delete_security_group(GroupId=sg["NativeRuleId"])

def configure_nebula(instance):
    subprocess.run('./nebula/nebula-cert ca -name "BLACKFISH" -out-crt nebula/ca/ca.crt -out-key nebula/ca/ca.key')
    subprocess.run('./nebula/nebula-cert sign -name "lighthouse" -ip "192.168.100.1" -ca-crt nebula/ca/ca.crt -ca-key nebula/ca/ca.key')
    subprocess.run('./nebula/nebula-cert sign -name "lp1" -ip "192.168.100.2" -ca-crt nebula/ca/ca.crt -ca-key nebula/ca/ca.key')
    subprocess.run('./nebula/nebula-cert sign -name "lp2" -ip "192.168.100.3"-ca-crt nebula/ca/ca.crt -ca-key nebula/ca/ca.key')
    subprocess.run('./nebula/nebula-cert sign -name "lp3" -ip "192.168.100.4" -ca-crt nebula/ca/ca.crt -ca-key nebula/ca/ca.key')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pk = paramiko.RSAKey.from_private_key(io.StringIO(kp_metadata['KeyMaterial']))
    time.sleep(30)
    client.connect(i.public_ip_address, username='ubuntu', pkey=pk)
    scp_client = scp.SCPClient(client.get_transport())
    with open("routes/redirectors/nginx_setup.sh", "r+") as f:
        for cmd in f.readlines():
            if cmd[:3]=="SCP":
                _, src, dest = cmd.split()
                scp_client.put(src, dest, recursive=True)
            else:
                stdin, stdout, stderr = client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                if exit_status!=0:
                    print("ERROR: remote command failed")
                    print(cmd)
