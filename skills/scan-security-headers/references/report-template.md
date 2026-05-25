# Security Headers Scan Report

## Scope

- Skill: `scan-security-headers`
- Target: `{{target}}`
- Date: `{{date}}`
- Evidence reviewed: `{{evidence_summary}}`

## Summary

| Severity | Findings |
|----------|----------|
| Critical | {{summary.critical}} |
| High | {{summary.high}} |
| Medium | {{summary.medium}} |
| Low | {{summary.low}} |
| Info | {{summary.info}} |

{{#if no_findings}}
No findings were identified from the available evidence.
{{/if}}

## Findings

{{#each findings}}
### {{id}} - {{name}}

- Severity: {{severity}}
- Category: {{category}}
- Evidence: `{{evidence}}`
- Location: `{{location}}`
- Risk: {{risk}}
- Remediation: {{remediation}}
{{/each}}

## Evidence Gaps

{{#each evidence_gaps}}
- {{gap}}
{{/each}}
