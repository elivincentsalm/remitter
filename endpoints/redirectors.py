import boto3
import json
import os
import uuid
from dotenv import load_dotenv, find_dotenv
from flask import Blueprint, request, abort
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
            instances = [serialize(i) for i in list(ec2_resource.instances.all())]
            return instances
        elif request.method=="POST":
            # minimum required parameters: [type: "http"]
            create_aws_redirector()
            status = {"status": "error"}
            return status
        elif request.method=="DELETE":
            # terminate all instances & associated resources
            # this is way too slow to run without a task queue. even an async request will timeout after 60 seconds
            delete_aws_redirectors()
            status = {"status": "error"}
            return status
    else:
        if redirector_id=="test":
            abort(404)
        instance = ec2_resouce.Instance(redirector_id)
        if request.method=="GET":
            return serialize(instance)
        elif request.method=="DELETE":
            instance.terminate()
            

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
    # run configuration script upon completion in background
    # can do this with rq
    configure_aws_redirector(instances[0])


def configure_aws_redirector(instance):
    #instance.wait_until_running()
    # run ansible setup on instance
    # could just run an os command
    pass


def delete_aws_redirectors():
    data = g.run('MATCH (r:Redirector) RETURN DISTINCT r;').data()
    print(json.dumps(data, indent=4))
    for r in data:
        instance_id = r["r"]["InstanceId"]
        ssh_key = g.run('MATCH (kp:KeyPair)-[]->(r:Redirector {InstanceId: "' + instance_id + '"}) RETURN kp;').data()[0]["kp"]
        sg = g.run('MATCH (sg:FirewallRuleset)-[]->(r:Redirector {InstanceId: "' + instance_id + '"}) RETURN sg;').data()[0]["sg"]
        instance = ec2_resource.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
        ec2_client.delete_key_pair(KeyName=ssh_key["KeyName"])
        ec2_client.delete_security_group(GroupId=sg["NativeRuleId"])
