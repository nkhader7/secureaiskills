# detect-secrets Report

| Field | Value |
|-------|-------|
| Skill | detect-secrets |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Files Scanned | {{file_count}} |
| Secrets Found | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} — {{rule_name}}

**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**Description:** {{description}}

```
{{snippet_masked}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No secrets or credentials were detected in the scanned files.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Immediate Actions

- **Rotate every Critical and High secret now** — assume any committed secret is compromised, regardless of whether the branch was merged.
- Check `git log --all -S "<secret>"` to confirm whether the secret appears in earlier commits; if so, rewrite history with `git filter-repo`.
- Add detected file types or variable names to `.gitignore` and pre-commit hooks (e.g., `detect-secrets`, `trufflehog`) to prevent recurrence.
- **Medium** and **Low** findings should be reviewed and remediated before the next release.
