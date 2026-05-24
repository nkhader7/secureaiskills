# scan-iac-security Report

| Field | Value |
|-------|-------|
| Skill | scan-iac-security |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Reviewed | {{file_count}} |
| IaC Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} — {{rule_name}}

**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**Description:** {{description}}

```
{{snippet}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No IaC security issues were detected in the reviewed files.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Review Focus

- Address all **Critical** and **High** findings before deployment.
- Review public exposure, wildcard IAM, encryption, and inline secret findings before merge.
- Document accepted risk for intentional public access or broad permissions.
- Use provider-native policy checks or SAST/IaC scanners as a second pass when available.
