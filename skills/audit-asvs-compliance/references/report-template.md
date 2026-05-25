# audit-asvs-compliance Report

| Field | Value |
|-------|-------|
| Skill | audit-asvs-compliance |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| ASVS Version | 5.0.0 |
| Scope | {{scope}} |
| ASVS Level | {{asvs_level}} |
| Requirements Reviewed | {{requirements_reviewed}} |
| Overall Status | {{overall_status}} |

---

## Findings

{{#each findings}}
### [{{status}}] {{rule_id}} - {{rule_name}}

**ASVS ID:** {{asvs_id}}
**ASVS Level:** {{asvs_level}}
**Chapter:** {{chapter_id}} - {{chapter_name}}
**Section:** {{section_id}} - {{section_name}}
**Severity:** {{severity}}

**Requirement:** {{description}}

**Evidence:** {{evidence}}

**Gap:** {{gap}}

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No ASVS gaps were identified from the reviewed evidence.
{{/if}}

## Summary Table

| Status | Count |
|--------|-------|
| Pass | {{count_pass}} |
| Partial | {{count_partial}} |
| Fail | {{count_fail}} |
| Unknown | {{count_unknown}} |
| Not Applicable | {{count_not_applicable}} |

## Level Summary

| ASVS Level | Reviewed | Pass | Partial | Fail | Unknown | Not Applicable |
|------------|----------|------|---------|------|---------|----------------|
| Level 1 | {{l1_reviewed}} | {{l1_pass}} | {{l1_partial}} | {{l1_fail}} | {{l1_unknown}} | {{l1_not_applicable}} |
| Level 2 | {{l2_reviewed}} | {{l2_pass}} | {{l2_partial}} | {{l2_fail}} | {{l2_unknown}} | {{l2_not_applicable}} |
| Level 3 | {{l3_reviewed}} | {{l3_pass}} | {{l3_partial}} | {{l3_fail}} | {{l3_unknown}} | {{l3_not_applicable}} |

## Review Focus

- Fix **Fail** results for in-scope Level 1 and Level 2 requirements before release.
- Convert **Unknown** results into evidence-backed `Pass`, `Partial`, `Fail`, or `Not Applicable` decisions.
- Track each accepted gap with an owner, due date, and compensating controls.
- Re-run the ASVS audit when authentication, authorization, input handling, API behavior, deployment architecture, or sensitive data handling changes.
