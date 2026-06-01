---
name: detect-secrets
format: markdown
description: Detects hardcoded secrets, credentials, and sensitive tokens committed to source code
triggers:
  - /detect-secrets
---

# detect-secrets

Detects hardcoded secrets, API keys, private keys, tokens, and credentials.

## Rules

### DS-001 — AWS Access Key (Critical)
Patterns: `AKIA[0-9A-Z]{16}`, `aws_secret_access_key\s*=\s*['\"]?[A-Za-z0-9/+=]{40}`
Remediation: Revoke in AWS IAM. Store in Secrets Manager.

### DS-002 — GCP Service Account Key (Critical)
Patterns: `"type":\s*"service_account"`, `"private_key":\s*"-----BEGIN`
Remediation: Delete in GCP IAM. Use Workload Identity Federation.

### DS-003 — Azure Client Secret (Critical)
Patterns: `AZURE_CLIENT_SECRET\s*=\s*['"][^'"]{20,}`, `client_secret\s*=\s*['"][A-Za-z0-9~._\-]{30,}`
Remediation: Rotate in Azure AD. Use Key Vault.

### DS-004 — Private Key Material (Critical)
Patterns: `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN EC PRIVATE KEY-----`, `-----BEGIN OPENSSH PRIVATE KEY-----`
Remediation: Revoke and regenerate. Use secrets manager.

### DS-005 — Stripe Secret Key (Critical)
Patterns: `sk_live_[A-Za-z0-9]{24,}`, `sk_test_[A-Za-z0-9]{24,}`
Remediation: Roll key in Stripe Dashboard. Use environment variables.

### DS-006 — GitHub PAT (High)
Patterns: `ghp_[A-Za-z0-9]{36}`, `github_pat_[A-Za-z0-9_]{82}`
Remediation: Revoke at github.com/settings/tokens.

### DS-007 — Slack Token (High)
Patterns: `xoxb-[0-9A-Za-z\-]{50,}`, `xoxp-[0-9A-Za-z\-]{50,}`
Remediation: Revoke in Slack app management console.

### DS-008 — Generic API Key Assignment (High)
Patterns: `(api_key|apikey|api_token|access_token)\s*=\s*['"][A-Za-z0-9_\-]{20,}['"]`
Remediation: Move to environment variables or secrets manager.

### DS-009 — Database Password Assignment (High)
Patterns: `(password|passwd|db_pass|db_password)\s*=\s*['"][^'"]{8,}['"]`
Remediation: Use connection string from environment. Never hardcode passwords.

### DS-010 — JWT Secret (High)
Patterns: `(jwt_secret|jwt_key|token_secret)\s*=\s*['"][^'"]{16,}['"]`, `jwt\.sign\([^,]+,\s*['"][^'"]{8,}['"]`
Remediation: Use long random secret from environment variable.

### DS-011 — npm Registry Token (Medium)
Patterns: `//registry\.npmjs\.org/:_authToken\s*=\s*[A-Za-z0-9\-_]{30,}`
Remediation: Use npm login with CI secrets store.

### DS-012 — Docker Registry Credential (Medium)
Patterns: `docker login.*-p\s+\S+`, `DOCKER_PASSWORD\s*=\s*['"][^'"]{8,}['"]`
Remediation: Use docker credential helpers or CI secrets.

### DS-013 — SSH Private Key (Critical)
Patterns: `-----BEGIN DSA PRIVATE KEY-----`, `-----BEGIN PRIVATE KEY-----`
Remediation: Remove from repo immediately. Rotate key pair.

### DS-014 — Hardcoded Connection String (High)
Patterns: `(mongodb|postgres|mysql|redis):\/\/[^:]+:[^@]+@`, `Server=.*;Password=[^;]{8,}`
Remediation: Use environment variable for full connection string.

### DS-015 — SendGrid API Key (High)
Patterns: `SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}`
Remediation: Revoke in SendGrid dashboard. Use environment variables.

## Orchestration

1. Collect target files (git diff or path argument).
2. Skip binaries, lock files, .gitignore entries.
3. Match each line against all rule patterns (regex).
4. Record file, line, rule ID, severity, masked snippet.
5. Sort findings Critical → High → Medium → Low.
6. Render report with summary table and immediate actions.
