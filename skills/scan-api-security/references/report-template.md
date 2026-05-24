# scan-api-security Report

| Field | Value |
|-------|-------|
| Skill | scan-api-security |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Reviewed | {{file_count}} |
| API Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} — {{rule_name}}

**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**OWASP API 2023:** {{owasp_api_2023_category}}
**Description:** {{description}}

```
{{snippet}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No API security issues were detected in the reviewed files.
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

- Address **Critical** and **High** findings before exposing the API.
- Validate authentication, authorization, and CORS configuration for internet-facing endpoints.
- Review **Medium** findings during API hardening and document accepted risk.
- Restrict documentation and debug endpoints to internal audiences.
