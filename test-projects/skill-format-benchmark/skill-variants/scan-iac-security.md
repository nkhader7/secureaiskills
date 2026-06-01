---
name: scan-iac-security
format: markdown
description: Scans Terraform, CloudFormation, Bicep, Pulumi, and Kubernetes IaC files for security misconfigurations
triggers:
  - /scan-iac-security
  - "scan.*iac"
  - "check.*terraform"
---

# scan-iac-security

Scan infrastructure-as-code files for security misconfigurations before deployment.

## Rules

### IAC-SG-001 — Open Security Group Inbound (Critical)
Patterns: `cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]`, `CidrIp:\s*"0\.0\.0\.0/0"`, `sourceAddressPrefix:\s*['"]\*['"]`
Remediation: Restrict ingress to known CIDR ranges. Never use 0.0.0.0/0 except for HTTP/HTTPS on load balancers.

### IAC-SG-002 — SSH Open to Internet (Critical)
Patterns: `from_port\s*=\s*22.*cidr_blocks.*0\.0\.0\.0`, `FromPort.*22.*CidrIp.*0\.0\.0\.0`
Remediation: Restrict SSH to bastion host IP. Use AWS Systems Manager Session Manager instead.

### IAC-S3-001 — Public S3 Bucket (Critical)
Patterns: `acl\s*=\s*["']public-read`, `AccessControl.*PublicRead`, `Principal.*"\*"`
Remediation: Remove public ACL. Enable S3 Block Public Access. Use CloudFront for public assets.

### IAC-S3-002 — S3 Encryption Disabled (High)
Patterns: `versioning_configuration\s*\{[^}]*status\s*=\s*"Disabled"`, `VersioningConfiguration.*Suspended`
Remediation: Enable S3 versioning and server-side encryption with AES-256 or KMS.

### IAC-RDS-001 — RDS Publicly Accessible (Critical)
Patterns: `publicly_accessible\s*=\s*true`, `PubliclyAccessible:\s*true`
Remediation: Set publicly_accessible = false. Place RDS in private subnet with security group.

### IAC-RDS-002 — RDS Encryption Disabled (High)
Patterns: `storage_encrypted\s*=\s*false`, `StorageEncrypted:\s*false`
Remediation: Enable storage_encrypted = true. Use aws_kms_key for customer-managed keys.

### IAC-RDS-003 — RDS No Deletion Protection (High)
Patterns: `deletion_protection\s*=\s*false`, `backup_retention_period\s*=\s*0`
Remediation: Set deletion_protection = true. Set backup_retention_period >= 7.

### IAC-IAM-001 — IAM Wildcard Action (Critical)
Patterns: `Action\s*=\s*"\*"`, `"Action":\s*"\*"`, `Action.*"\*".*Resource.*"\*"`
Remediation: Use least-privilege IAM policies. Enumerate specific actions needed.

### IAC-IAM-002 — IAM Wildcard Principal (Critical)
Patterns: `Principal\s*=\s*"\*"`, `"Principal":\s*"\*"`, `Principal.*"\*".*Action`
Remediation: Never use Principal = "*". Specify exact AWS account IDs, roles, or services.

### IAC-EBS-001 — EBS Volume Unencrypted (High)
Patterns: `encrypted\s*=\s*false`, `Encrypted:\s*false`
Remediation: Set encrypted = true. Enable default EBS encryption per region.

### IAC-K8S-001 — Privileged Container (Critical)
Patterns: `privileged:\s*true`, `allowPrivilegeEscalation:\s*true`
Remediation: Set privileged: false and allowPrivilegeEscalation: false in securityContext.

### IAC-K8S-002 — Host Namespace Sharing (Critical)
Patterns: `hostNetwork:\s*true`, `hostPID:\s*true`, `hostIPC:\s*true`
Remediation: Never share host namespaces. Use dedicated pod networking.

### IAC-K8S-003 — Running as Root (High)
Patterns: `runAsUser:\s*0`, `runAsNonRoot:\s*false`
Remediation: Set runAsNonRoot: true and runAsUser to a non-zero UID >= 1000.

### IAC-K8S-004 — Wildcard RBAC Verbs (Critical)
Patterns: `verbs:\s*\["\*"\]`, `resources:\s*\["\*"\].*verbs`, `apiGroups:\s*\["\*"\]`
Remediation: Enumerate specific RBAC verbs and resources. Avoid cluster-admin role binding.

### IAC-K8S-005 — Docker Socket Mounted (Critical)
Patterns: `path:\s*/var/run/docker\.sock`, `docker\.sock`
Remediation: Never mount the Docker socket. Use a dedicated container runtime API.

### IAC-K8S-006 — Secrets in ConfigMap (High)
Patterns: `(password|api_key|secret|token)\s*:\s*["'][^"']{8,}["']`
Remediation: Move secrets to Kubernetes Secrets or external secrets manager.

### IAC-CFN-001 — CloudTrail Logging Disabled (High)
Patterns: `IsLogging:\s*false`, `EnableLogFileValidation:\s*false`
Remediation: Enable CloudTrail logging and log file validation in all regions.

### IAC-LAMBDA-001 — Lambda Plaintext Env Secrets (High)
Patterns: `(DB_PASSWORD|API_SECRET|JWT_SECRET|STRIPE_SECRET)\s*=\s*["'][^"']{6,}["']`
Remediation: Use AWS Secrets Manager or SSM Parameter Store. Reference secrets by ARN.

### IAC-TFVAR-001 — Secrets in tfvars (Critical)
Patterns: `(password|secret|api_key|private_key)\s*=\s*["'][^"']{8,}["']`
Remediation: Never commit secrets to tfvars. Use Vault, AWS Secrets Manager, or env vars.

### IAC-BICEP-001 — Azure Storage Public Access (High)
Patterns: `allowBlobPublicAccess:\s*true`, `supportsHttpsTrafficOnly:\s*false`, `minimumTlsVersion:\s*'TLS1_0'`
Remediation: Set allowBlobPublicAccess: false and supportsHttpsTrafficOnly: true.

## Orchestration

1. Collect IaC files (*.tf, *.tfvars, *.yaml, *.yml, *.json, *.bicep, *.py for Pulumi).
2. Skip .terraform/, node_modules/, lock files, and build output.
3. Match each line against all rule patterns (regex).
4. Record file, line, rule ID, severity, masked snippet.
5. Sort Critical → High → Medium → Low.
6. Render report with per-framework sections.
