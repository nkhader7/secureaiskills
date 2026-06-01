# scan-iac-security fixture — AWS storage misconfigurations
# Intentionally vulnerable — do not deploy

# IAC-S3-001: public S3 bucket with public-read ACL
resource "aws_s3_bucket" "public_data" {
  bucket = "company-public-data-bucket"
  acl    = "public-read"           # IAC-S3-001: publicly readable
}

# IAC-S3-002: S3 bucket with public-read-write ACL
resource "aws_s3_bucket" "public_write" {
  bucket = "company-upload-bucket"
  acl    = "public-read-write"     # IAC-S3-002: world-writable
}

# IAC-S3-003: S3 versioning disabled
resource "aws_s3_bucket_versioning" "public_data" {
  bucket = aws_s3_bucket.public_data.id
  versioning_configuration {
    status = "Disabled"            # IAC-S3-003: no version history
  }
}

# IAC-S3-004: S3 server-side encryption disabled (no aws_s3_bucket_server_side_encryption_configuration)
resource "aws_s3_bucket" "unencrypted_logs" {
  bucket = "company-unencrypted-logs"
  # No server_side_encryption_configuration block
}

# IAC-S3-005: S3 block public access settings not configured
resource "aws_s3_bucket" "no_public_block" {
  bucket = "company-assets"
  # No aws_s3_bucket_public_access_block resource defined
}

# IAC-EBS-001: EBS volume without encryption
resource "aws_ebs_volume" "unencrypted" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = false        # IAC-EBS-001: data at rest unencrypted
}

# IAC-EBS-002: EBS snapshot public
resource "aws_ebs_snapshot_copy" "public_snap" {
  source_snapshot_id = "snap-0123456789abcdef0"
  source_region      = "us-east-1"
}

resource "aws_snapshot_create_volume_permission" "make_public" {
  snapshot_id = aws_ebs_snapshot_copy.public_snap.id
  account_id  = "all"             # IAC-EBS-002: snapshot shared publicly
}

# IAC-RDS-001: RDS instance publicly accessible and unencrypted
resource "aws_db_instance" "public_db" {
  identifier             = "prod-database"
  engine                 = "postgres"
  instance_class         = "db.t3.medium"
  allocated_storage      = 50
  username               = "dbadmin"
  password               = "hardcoded_db_password_123"  # plaintext secret
  publicly_accessible    = true    # IAC-RDS-001: exposed to internet
  storage_encrypted      = false   # IAC-RDS-002: no encryption at rest
  deletion_protection    = false   # IAC-RDS-003: no deletion guard
  backup_retention_period = 0      # IAC-RDS-004: no automated backups
  skip_final_snapshot    = true
  multi_az               = false
}
