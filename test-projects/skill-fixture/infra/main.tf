resource "aws_security_group" "public_ssh" {
  name = "public-ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "public_data" {
  bucket = "skill-fixture-public-data"
  acl    = "public-read"
}

resource "aws_ebs_volume" "plain" {
  availability_zone = "us-east-1a"
  size              = 10
  encrypted         = false
}
