provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region = "us-east-1"
}

resource "aws_instance" "http-redir" {
  ami = "ami-052efd3df9dad4825"
  instance_type = "t2.micro"
}
