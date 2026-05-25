# Vulnerable Package Report

## Scope

- Skill: `scan-sca-dependencies`
- Target: `{{target}}`
- Date: `{{date}}`
- Evidence reviewed: `{{evidence_summary}}`
- Scanner/source: `{{scanner_summary}}`
- Vulnerability database updated: `{{database_updated_at}}`
- Generated: `{{generated_at}}`

## Summary

| Severity | Findings | Packages | Fix Available | Known Exploited | Unknown Fix |
|----------|----------|----------|---------------|-----------------|-------------|
| Critical | {{summary.critical.findings}} | {{summary.critical.packages}} | {{summary.critical.fix_available}} | {{summary.critical.known_exploited}} | {{summary.critical.unknown_fix}} |
| High | {{summary.high.findings}} | {{summary.high.packages}} | {{summary.high.fix_available}} | {{summary.high.known_exploited}} | {{summary.high.unknown_fix}} |
| Medium | {{summary.medium.findings}} | {{summary.medium.packages}} | {{summary.medium.fix_available}} | {{summary.medium.known_exploited}} | {{summary.medium.unknown_fix}} |
| Low | {{summary.low.findings}} | {{summary.low.packages}} | {{summary.low.fix_available}} | {{summary.low.known_exploited}} | {{summary.low.unknown_fix}} |
| Unknown | {{summary.unknown.findings}} | {{summary.unknown.packages}} | {{summary.unknown.fix_available}} | {{summary.unknown.known_exploited}} | {{summary.unknown.unknown_fix}} |

## Findings

{{#each findings}}
### {{severity}} - {{package_name}} {{package_version}} - {{cve}}

- Package: `{{package_name}}`
- Version: `{{package_version}}`
- Ecosystem: `{{package_type}}`
- Dependency Type: `{{dependency_type}}`
- Dependency Path: `{{dependency_path}}`
- Source: `{{source}}`
- Advisory: `{{cve}}`
- Severity: `{{severity}}`
- CVSS: `{{cvss_score}}`
- Affected Range: `{{affected_range}}`
- Fixed Version: `{{fixed_version}}`
- Exploit Signal: `{{exploit_available}}`
- Reachability: `{{reachability}}`
- Evidence: `{{evidence}}`
- Remediation: `{{remediation}}`
{{/each}}

## No-Fix Findings

{{#each no_fix_findings}}
- `{{package_name}}` `{{package_version}}` - `{{cve}}` - {{severity}} - {{recommended_action}}
{{/each}}

## Evidence Gaps

{{#each evidence_gaps}}
- {{gap}}
{{/each}}

{{#if no_findings}}
No vulnerable packages were detected in the scanned dependency evidence.
{{/if}}

## Notes

Scanner results depend on vulnerability database freshness, package manager metadata quality, and whether the input includes development dependencies, transitive dependencies, image OS packages, and runtime-only packages.
