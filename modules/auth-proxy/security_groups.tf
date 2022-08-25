data "external" "get_public_ip" {
  program = ["bash", "../../scripts/get_public_ip.sh" ]
}

resource "aws_security_group" "auth-proxy-sg" {
  name = "auth-proxy-sg"

  ingress = [
    {
      description = "Allow SSH from home"
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = ["${data.external.get_public_ip.result["ip"]}/32"]
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
    }, {
      description = "Allow HTTP from ALL"
      from_port = 443
      to_port = 443
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      security_groups = []
      self = false
    }
  ]
}

// attach the security group
resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = aws_security_group.auth-proxy-sg.id
  network_interface_id = aws_instance.auth-proxy.primary_network_interface_id
}
