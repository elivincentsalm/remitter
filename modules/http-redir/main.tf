provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region = "us-east-1"
}

data "external" "get_public_ip" {
  program = ["bash", "../../scripts/get_public_ip.sh" ]
}

resource "aws_key_pair" "pub_key" {
  key_name = "pub_key"
  public_key = file("/users/elisalm/documents/remitter/keys/id_rsa.pub")
}

// create the redirector instance
resource "aws_instance" "http-redir" {
  ami = "ami-052efd3df9dad4825"             // ubuntu 22.04
  instance_type = "t2.micro"
  key_name = aws_key_pair.pub_key.key_name  // adding private key

  // runs ansible playbook to set up
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=false ansible-playbook -i playbooks/hosts -u ubuntu playbooks/setup.yml"
  }
}

// attach the security group
resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = aws_security_group.http-redir-sg.id
  network_interface_id = aws_instance.http-redir.primary_network_interface_id
}
