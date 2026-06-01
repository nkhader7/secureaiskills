# scan-iac-security fixture — AWS networking misconfigurations
# Intentionally vulnerable — do not deploy

# IAC-SG-001: security group allows all inbound traffic on all ports
resource "aws_security_group" "open_inbound" {
  name        = "open-inbound"
  description = "Allows all inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]    # IAC-SG-001: wildcard IPv4 inbound
  }

  ingress {
    from_port        = 0
    to_port          = 65535
    protocol         = "tcp"
    ipv6_cidr_blocks = ["::/0"]    # IAC-SG-001: wildcard IPv6 inbound
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAC-SG-002: SSH open to internet
resource "aws_security_group" "public_ssh" {
  name = "public-ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]    # IAC-SG-002: SSH exposed to internet
  }
}

# IAC-SG-003: RDP open to internet
resource "aws_security_group" "public_rdp" {
  name = "public-rdp"

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]    # IAC-SG-003: RDP exposed to internet
  }
}

# IAC-NW-001: VPC flow logs disabled
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  # No flow_log resource attached — logging disabled
}

# IAC-NW-002: Subnet maps public IP on launch
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true    # IAC-NW-002: all instances get public IPs
}

# IAC-NW-003: Internet gateway directly accessible
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}
