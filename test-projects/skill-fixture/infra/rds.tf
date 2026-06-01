# scan-iac-security fixture — RDS + IAM misconfigurations
# Intentionally vulnerable — do not deploy

# IAC: RDS instance publicly accessible, unencrypted, no deletion protection
resource "aws_db_instance" "vulnerable" {
  identifier             = "vulnerable-db"
  engine                 = "mysql"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = "appdb"
  username               = "admin"
  password               = "Passw0rd123!"     # hardcoded plaintext password
  publicly_accessible    = true               # exposed to internet
  storage_encrypted      = false              # data at rest unencrypted
  deletion_protection    = false              # can be deleted without safeguard
  backup_retention_period = 0                 # no automated backups
  skip_final_snapshot    = true
  multi_az               = false
}

# IAC: S3 bucket with public ACL and no versioning
resource "aws_s3_bucket" "logs" {
  bucket = "company-logs-public"
  acl    = "public-read-write"               # anyone can read and write
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Disabled"                       # no object versioning
  }
}

# IAC: overly permissive IAM policy — admin wildcard
resource "aws_iam_policy" "wildcard_admin" {
  name = "allow-everything"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"                          # all actions
      Resource = "*"                          # all resources
    }]
  })
}

# IAC: Lambda function with environment variable secrets in plaintext
resource "aws_lambda_function" "processor" {
  function_name = "data-processor"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "nodejs18.x"
  handler       = "index.handler"
  filename      = "function.zip"

  environment {
    variables = {
      DB_PASSWORD    = "hardcoded-db-pass"   # secret in plaintext
      API_SECRET_KEY = "stripe_live_fake_key_placeholder" # Stripe-like key pattern
    }
  }
}

# IAC: Security group allowing all inbound traffic
resource "aws_security_group" "allow_all" {
  name = "allow-all-inbound"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # all ports from internet
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
