# scan-xml-security Report

| Field | Value |
|-------|-------|
| Skill | scan-xml-security |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Reviewed | {{file_count}} |
| Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} - {{rule_name}}

**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**Description:** {{description}}

```xml
{{snippet}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No XML security issues were detected in the reviewed files.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High | {{count_high}} |
| Medium | {{count_medium}} |
| Low | {{count_low}} |
| Info | {{count_info}} |
