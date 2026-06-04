# Secrets Scan Report

| Field | Value |
|-------|-------|
| Skill | sample-secrets-scan |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Scanned | {{file_count}} |
| Total Findings | {{finding_count}} |
| Highest Severity | {{highest_severity}} |

---

## Findings

{{#each findings}}
### {{rule_id}} — {{severity}}

**File:** `{{file}}` — Line {{line}}

**Rule:** {{rule_name}}

**Evidence:**
```
{{snippet}}
```
*(value redacted)*

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No secrets or credentials detected in the scanned files.
{{/if}}

## Severity Summary

| Severity | Count |
|----------|-------|
| Critical | {{critical_count}} |
| High | {{high_count}} |
| Medium | {{medium_count}} |
| Low | {{low_count}} |
| Info | {{info_count}} |

## Recommended Actions

1. **Rotate all exposed credentials immediately** — treat any matched value as compromised.
2. Add a pre-commit hook or CI secret-scanning step to prevent future leaks.
3. Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) for all credentials.
