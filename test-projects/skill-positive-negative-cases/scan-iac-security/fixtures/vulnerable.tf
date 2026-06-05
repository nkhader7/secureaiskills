# VULNERABLE FIXTURE — scan-iac-security test

# IAC: Open SSH to world (0.0.0.0/0)
resource "aws_security_group" "open_ssh" {
  name = "open-ssh"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAC: S3 bucket with public ACL
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}

# IAC: RDS with no encryption
resource "aws_db_instance" "insecure_db" {
  identifier     = "prod-db"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  storage_encrypted = false
  publicly_accessible = true
  username = "admin"
  password = "plaintext-password-in-tf"
}

# IAC: EC2 instance with no IMDSv2 enforcement
resource "aws_instance" "no_imdsv2" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}
