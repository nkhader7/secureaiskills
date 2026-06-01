# scan-iac-security fixture — AWS compute misconfigurations
# Intentionally vulnerable — do not deploy

# IAC-EC2-001: EC2 instance with public IP and no IMDSv2
resource "aws_instance" "web_server" {
  ami                         = "ami-0c55b159cbfafe1f0"
  instance_type               = "t3.medium"
  associate_public_ip_address = true     # IAC-EC2-001: public IP assigned
  key_name                    = "prod-key"

  # IAC-EC2-002: no IMDSv2 enforcement
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"    # should be "required"
    http_put_response_hop_limit = 2
  }

  # IAC-EC2-003: EBS root volume not encrypted
  root_block_device {
    volume_size = 50
    encrypted   = false                  # IAC-EC2-003
  }

  # IAC-EC2-004: user_data with hardcoded credentials
  user_data = <<-EOF
    #!/bin/bash
    export DB_PASSWORD="hardcoded_secret_in_userdata"
    export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    echo "password=P@ssw0rd123" >> /etc/app.conf
  EOF
}

# IAC-LAMBDA-001: Lambda function with plaintext secrets in environment
resource "aws_lambda_function" "data_processor" {
  function_name = "data-processor"
  role          = aws_iam_role.open_assume.arn
  runtime       = "python3.11"
  handler       = "handler.main"
  filename      = "function.zip"

  environment {
    variables = {
      DB_PASSWORD       = "lambda_hardcoded_pass"   # IAC-LAMBDA-001
      STRIPE_SECRET_KEY = "stripe_live_fake_key_placeholder"  # IAC-LAMBDA-001
      JWT_SECRET        = "super_secret_jwt_key_123" # IAC-LAMBDA-001
    }
  }

  # IAC-LAMBDA-002: Lambda tracing disabled
  # No tracing_config block
}

# IAC-LAMBDA-003: Lambda with reserved concurrency = 0 (can be DDoSed to zero)
resource "aws_lambda_function" "api_handler" {
  function_name                  = "api-handler"
  role                           = aws_iam_role.open_assume.arn
  runtime                        = "nodejs18.x"
  handler                        = "index.handler"
  filename                       = "api.zip"
  reserved_concurrent_executions = 0   # IAC-LAMBDA-003: always throttled
}

# IAC-ECR-001: ECR repository with public image scan disabled
resource "aws_ecr_repository" "app" {
  name                 = "app-repository"
  image_tag_mutability = "MUTABLE"       # IAC-ECR-001: tags can be overwritten

  image_scanning_configuration {
    scan_on_push = false                 # IAC-ECR-002: no vulnerability scan
  }
}
