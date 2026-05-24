# scan-for-injection Report

| Field | Value |
|-------|-------|
| Skill | scan-for-injection |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Reviewed | {{file_count}} |
| Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} — {{rule_name}}

**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**Description:** {{description}}

```text
{{snippet}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No injection vulnerabilities were detected in the scanned files.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Next Steps

- Address all **Critical** and **High** findings before merging.
- Review **Medium** findings and apply fixes or document accepted risk.
- **Low** and **Info** items are advisory — fix at your discretion.
