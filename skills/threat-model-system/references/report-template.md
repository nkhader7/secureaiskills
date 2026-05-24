# threat-model-system Report

| Field | Value |
|-------|-------|
| Skill | threat-model-system |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Artifacts Reviewed | {{artifact_count}} |
| Threat Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## System Summary

**Scope:** {{scope}}

**Assets:** {{assets}}

**Actors:** {{actors}}

**Entry Points:** {{entry_points}}

**Trust Boundaries:** {{trust_boundaries}}

**Data Flows:** {{data_flows}}

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} - {{rule_name}}

**Component:** {{component}}
**Category:** {{category}}
**Threat Scenario:** {{threat_scenario}}
**Evidence:** {{evidence}}
**Impact:** {{impact}}
**Likelihood:** {{likelihood}}

**Recommended Mitigation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No material threat-model findings were identified from the reviewed system context.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Assumptions And Unknowns

{{assumptions}}

{{unknowns}}

## Review Focus

- Address all **Critical** and **High** findings before implementation or release.
- Resolve unknowns that block security decisions for authentication, authorization, data protection, or external exposure.
- Document accepted risks with an owner, expiration date, and compensating controls.
- Re-run the threat model when trust boundaries, privileged flows, or sensitive data handling changes.
