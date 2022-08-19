provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region = "us-east-1"
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
}

// create new ansible config and trigger execution of playbook
data "template_file" "hosts" {
  template = "${file("${path.module}/templates/hosts.tpl")}"
  depends_on = [
    aws_instance.http-redir,
  ]
  vars = {
    ip = "${aws_instance.http-redir.public_ip}"
  }
}

resource "null_resource" "hosts" {
  triggers = {
    template_rendered = "${data.template_file.hosts.rendered}"
  }
  provisioner "local-exec" {
    command = "echo '${data.template_file.hosts.rendered}' > playbooks/hosts"
  }
  provisioner "local-exec" {
    command = "sleep 30 && ANSIBLE_HOST_KEY_CHECKING=false ansible-playbook -i playbooks/hosts -u ubuntu playbooks/setup.yml"
  }
}
