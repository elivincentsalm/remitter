data "external" "get_public_ip" {
  program = ["bash", "../../scripts/get_public_ip.sh" ]
}

resource "aws_security_group" "dns-redir-sg" {
  name = "dns-redir-sg"

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
      description = "Allow DNS from ALL"
      from_port = 53
      to_port = 53
      protocol = "udp"
      cidr_blocks = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      security_groups = []
      self = false
    }
  ]

  egress = [
    {
      description = "Allow forwarding to DNS"
      from_port = 53
      to_port = 53
      protocol = "udp"
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
  security_group_id    = aws_security_group.dns-redir-sg.id
  network_interface_id = aws_instance.dns-redir.primary_network_interface_id
}
