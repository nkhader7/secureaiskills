# scan-for-ssrf Report

| Field | Value |
|-------|-------|
| Skill | scan-for-ssrf |
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
No SSRF vulnerabilities were detected in the scanned files.
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
- Critical findings indicate direct user-controlled HTTP sinks or metadata endpoint access — treat as exploitable until proven otherwise.
- For **Medium** findings, review whether DNS rebinding mitigations and redirect-following controls are in place.
- Apply allowlist-based URL validation at every outbound request boundary.
- Consider network-level controls (egress proxy, VPC security groups) as a defence-in-depth layer.
