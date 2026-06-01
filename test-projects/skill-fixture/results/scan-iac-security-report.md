# scan-iac-security Report

| Field | Value |
|-------|-------|
| Skill | scan-iac-security |
| Target | test-projects/skill-fixture/infra/main.tf |
| Date | 2026-05-25 |
| Branch | main |
| Files Reviewed | 1 |
| IaC Findings | 3 |
| Overall Severity | Critical |

---

## Findings

### [Critical] IAC-001 - Public SSH Access

**File:** `test-projects/skill-fixture/infra/main.tf` (line 8)
**Category:** Network Exposure
**Description:** Security group rule allows SSH from the public internet.

```hcl
resource "aws_security_group" "public_ssh" {
  name = "public-ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Remediation:** Restrict SSH to trusted administrative networks or remove direct SSH access in favor of a bastion, SSM, VPN, or just-in-time access.

---

### [High] IAC-004 - Public Object Storage Access

**File:** `test-projects/skill-fixture/infra/main.tf` (line 14)
**Category:** Storage
**Description:** Object storage bucket is configured for public access.

```hcl
resource "aws_s3_bucket" "public_data" {
  bucket = "skill-fixture-public-data"
  acl    = "public-read"
}
```

**Remediation:** Disable public access by default and use explicit, reviewed exceptions for public assets.

---

### [High] IAC-005 - Storage Encryption Disabled

**File:** `test-projects/skill-fixture/infra/main.tf` (line 20)
**Category:** Encryption
**Description:** Storage resource is configured without encryption at rest.

```hcl
resource "aws_ebs_volume" "plain" {
  availability_zone = "us-east-1a"
  size              = 10
  encrypted         = false
}
```

**Remediation:** Enable encryption at rest using provider-managed keys at minimum, and use customer-managed keys for sensitive workloads.

---

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 2 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

## Review Focus

- Address the public SSH finding before deployment.
- Review whether the S3 bucket is intentionally public; if so, document the exception and enforce public access blocks elsewhere.
- Enable EBS encryption or set an account-level default encryption policy.
