# Supply Chain Risk Report

## Scope

- Skill: `detect-supply-chain-risks`
- Target: `{{target}}`
- Date: `{{date}}`
- Evidence reviewed: `{{evidence_summary}}`
- Generated: `{{generated_at}}`

## Summary

| Severity | Findings | CI/CD | Dependencies | Containers | Artifacts | Registry |
|----------|----------|------|--------------|------------|-----------|----------|
| Critical | {{summary.critical.findings}} | {{summary.critical.cicd}} | {{summary.critical.dependencies}} | {{summary.critical.containers}} | {{summary.critical.artifacts}} | {{summary.critical.registry}} |
| High | {{summary.high.findings}} | {{summary.high.cicd}} | {{summary.high.dependencies}} | {{summary.high.containers}} | {{summary.high.artifacts}} | {{summary.high.registry}} |
| Medium | {{summary.medium.findings}} | {{summary.medium.cicd}} | {{summary.medium.dependencies}} | {{summary.medium.containers}} | {{summary.medium.artifacts}} | {{summary.medium.registry}} |
| Low | {{summary.low.findings}} | {{summary.low.cicd}} | {{summary.low.dependencies}} | {{summary.low.containers}} | {{summary.low.artifacts}} | {{summary.low.registry}} |

## Findings

{{#each findings}}
### {{id}} - {{name}}

- Severity: {{severity}}
- Category: {{category}}
- Asset: `{{asset}}`
- Evidence: `{{evidence}}`
- Trust Boundary: {{trust_boundary}}
- Attack Scenario: {{attack_scenario}}
- Impact: {{impact}}
- Remediation: {{remediation}}
{{/each}}

## Integrity and Provenance Gaps

{{#each provenance_gaps}}
- {{gap}}
{{/each}}

{{#if no_findings}}
No supply chain risk indicators were detected in the reviewed evidence.
{{/if}}

## Notes

This report identifies ways the build, dependency, release, or deployment chain can be tampered with. Known vulnerable package CVEs should be reported through `scan-sca-dependencies`.
