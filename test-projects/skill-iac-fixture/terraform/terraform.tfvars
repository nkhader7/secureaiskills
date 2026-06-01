# scan-iac-security fixture — tfvars with hardcoded secrets
# Intentionally vulnerable — do not deploy

region       = "us-east-1"
environment  = "production"

# IAC-TFVAR-001: database password in tfvars
db_password  = "TfVars_DB_P@ssword_123"

# IAC-TFVAR-002: API keys committed in tfvars
api_key      = "AWS_ACCESS_KEY_ID_EXAMPLE_PLACEHOLDER"
api_secret   = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYSECRETKEY"

# IAC-TFVAR-003: private key path pointing to embedded key
private_key  = "-----BEGIN RSA PRIVATE KEY-----"

# IAC-TFVAR-004: JWT secret
jwt_secret   = "my_super_secret_jwt_signing_key_32chars"

# IAC-TFVAR-005: webhook secret
webhook_secret = "whsec_fixture_webhook_secret_key_here"

allowed_cidrs = ["0.0.0.0/0"]    # IAC-TFVAR-006: unrestricted CIDR
