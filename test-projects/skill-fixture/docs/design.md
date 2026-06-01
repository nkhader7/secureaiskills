# Skill Fixture Design Notes

This document is intentionally incomplete so design and ASVS skills have
evidence to review.

## System Boundary

The application accepts browser traffic, API clients, GitHub Actions builds,
container image builds, Kubernetes deployment manifests, Terraform, and SBOM
inputs. Trust boundaries are TBD.

## Security Assumptions

- No abuse cases have been documented.
- No documented data classification exists for user records, reset tokens, or
  tenant invoices.
- Missing authorization is accepted for the prototype.
- Session cookie security is not finalized.
- ASVS Level 2 compliance is desired, but no evidence map exists.
- No central alerting or SIEM integration exists.
- Logging may include passwords and reset tokens during debugging.
