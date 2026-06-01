# scan-iac-security fixture — AWS IAM misconfigurations
# Intentionally vulnerable — do not deploy

# IAC-IAM-001: IAM policy with wildcard Action and Resource
resource "aws_iam_policy" "admin_wildcard" {
  name        = "full-admin-access"
  description = "Grants all permissions"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"               # IAC-IAM-001: all actions
      Resource = "*"               # IAC-IAM-001: all resources
    }]
  })
}

# IAC-IAM-002: inline IAM policy attached directly to user (not via group/role)
resource "aws_iam_user_policy" "inline" {
  name = "inline-user-policy"
  user = "deploy-user"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:*", "ec2:*", "iam:*"]
      Resource = "*"
    }]
  })
}

# IAC-IAM-003: IAM role with overly permissive assume-role (anyone can assume)
resource "aws_iam_role" "open_assume" {
  name = "open-assume-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"              # IAC-IAM-003: anyone can assume this role
      Action    = "sts:AssumeRole"
    }]
  })
}

# IAC-IAM-004: IAM access key created with no rotation policy
resource "aws_iam_access_key" "no_rotation" {
  user   = "ci-user"
  status = "Active"
  # No rotation schedule / lifecycle rule
}

# IAC-IAM-005: Root account access key (simulated via naming)
resource "aws_iam_user" "root_like" {
  name = "root-admin"
  path = "/"
  # Console access with no MFA enforcement
}

# IAC-KMS-001: KMS key with public access policy
resource "aws_kms_key" "public_key" {
  description             = "Customer key"
  deletion_window_in_days = 7
  enable_key_rotation     = false   # IAC-KMS-001: no automatic rotation
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "*" }     # IAC-KMS-002: public key policy
      Action    = "kms:*"
      Resource  = "*"
    }]
  })
}
