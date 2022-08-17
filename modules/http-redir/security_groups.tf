resource "aws_security_group" "http-redir-sg" {
  name = "http-redir-sg"

  ingress = [
    {
      description = "Allow SSH from home"
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = ["${data.external.get_public_ip.result["ip"]}/32"]
      // cidr_blocks = ["0.0.0.0/0"]
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
