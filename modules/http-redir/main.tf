provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region = "us-east-1"
}

data "external" "get_public_ip" {
  program = ["bash", "../../scripts/get_public_ip.sh" ]
}

resource "aws_key_pair" "ssh_key" {
  key_name = "ssh_key"
  public_key = file("/Users/elisalm/Documents/remitter/keys/id_rsa.pub")
}

resource "aws_instance" "http-redir" {
  ami = "ami-052efd3df9dad4825"
  instance_type = "t2.micro"
  key_name = aws_key_pair.ssh_key.key_name

  user_data = <<EOF
#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y apache2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
sudo a2enmod rewrite proxy proxy_http
sudo sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf
sudo systemctl start apache2
sudo systemctl enable apache2
  EOF
  
  /*
  provisioner "file" {
    source = "./files/apache2.conf"
    destination = "/etc/apache2/apache2.conf"
  }

  provisioner "file" {
    source = "./files/.htaccess"
    destination = "/var/www/html/.htaccess"
  }
  */

}

resource "aws_security_group" "http-redir-sg" {
  name = "http-redir-sg"

  ingress = [
    {
      description = "Allow SSH from home"
      from_port = 22
      to_port = 22
      protocol = "tcp"
      // cidr_blocks = ["${data.external.get_public_ip.result["ip"]}/32"]
      cidr_blocks = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      security_groups = []
      self = false
    }, {
      description = "Allow HTTP from ALL"
      from_port = 80
      to_port = 80
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      security_groups = []
      self = false
    }
  ]
}

resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = aws_security_group.http-redir-sg.id
  network_interface_id = aws_instance.http-redir.primary_network_interface_id
}
