import io
import subprocess
import paramiko
import scp
from py2neo import Graph

neo4j_uri = "bolt://neo4j:password@localhost:7687"
g = Graph(neo4j_uri)
key = g.run("MATCH (a:KeyPair)-[:BELONGS_TO]->(:Redirector {InstanceId: 'i-0d6fb594f17234651'}) RETURN a;").data()[0]["a"]["KeyMaterial"]

subprocess.run('./nebula/nebula-cert ca -name "BLACKFISH" -out-crt nebula/ca/ca.crt -out-key nebula/ca/ca.key', shell=True)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
pk = paramiko.RSAKey.from_private_key(io.StringIO(key))
client.connect("54.161.197.16", username='ubuntu', pkey=pk)
scp_client = scp.SCPClient(client.get_transport())

stdin, stdout, stderr = client.exec_command("sudo mkdir /etc/nebula")
exit_status = stdout.channel.recv_exit_status()

scp_client.put("nebula/configs/config-lighthouse.yaml", "config-lighthouse.yaml", recursive=True)

stdin, stdout, stderr = client.exec_command("sudo mv config-lighthouse.yaml /etc/nebula/config.yaml")
exit_status = stdout.channel.recv_exit_status()

subprocess.run('./nebula/nebula-cert sign -name "lighthouse" -ca-crt nebula/ca/ca.crt -ca-key nebula/ca/ca.key -ip "192.168.100.1/24" -out-crt nebula/tmp/host.crt -out-key nebula/tmp/host.key', shell=True)

scp_client.put("nebula/ca/ca.crt", "ca.crt", recursive=True)

stdin, stdout, stderr = client.exec_command("sudo mv ca.crt /etc/nebula/ca.crt")
exit_status = stdout.channel.recv_exit_status()

scp_client.put("nebula/tmp/host.crt", "host.crt", recursive=True)

stdin, stdout, stderr = client.exec_command("sudo mv host.crt /etc/nebula/host.crt")
exit_status = stdout.channel.recv_exit_status()

scp_client.put("nebula/tmp/host.key", "host.key", recursive=True)

stdin, stdout, stderr = client.exec_command("sudo mv host.key /etc/nebula/host.key")
exit_status = stdout.channel.recv_exit_status()

scp_client.put("nebula/nebula", "nebula", recursive=True)

stdin, stdout, stderr = client.exec_command("sudo ./nebula -config /etc/nebula/config.yaml")
