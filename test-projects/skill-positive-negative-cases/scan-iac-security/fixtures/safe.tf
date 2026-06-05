# SAFE FIXTURE — scan-iac-security test

resource "aws_security_group" "restricted_ssh" {
  name = "restricted-ssh"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}

resource "aws_s3_bucket" "private_bucket" {
  bucket = "my-private-bucket"
}

resource "aws_s3_bucket_acl" "private" {
  bucket = aws_s3_bucket.private_bucket.id
  acl    = "private"
}

resource "aws_db_instance" "secure_db" {
  identifier            = "prod-db"
  engine                = "mysql"
  instance_class        = "db.t3.micro"
  storage_encrypted     = true
  publicly_accessible   = false
  password              = var.db_password
}

resource "aws_instance" "imdsv2_enforced" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  metadata_options {
    http_tokens = "required"
  }
}
