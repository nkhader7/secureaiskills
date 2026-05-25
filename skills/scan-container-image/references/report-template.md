# scan-container-image Report

| Field | Value |
|-------|-------|
| Skill | scan-container-image |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Benchmark | CIS Docker Benchmark v1.8.0 |
| Profile | {{profile}} |
| Files Reviewed | {{file_count}} |
| Controls Reviewed | {{controls_reviewed}} |
| Overall Severity | {{overall_severity}} |

---

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} - {{rule_name}}

**Recommendation:** {{recommendation_id}}
**Profile:** {{profile}}
**Assessment:** {{assessment_status}}
**Section:** {{section_id}} - {{section_name}}
**Status:** {{status}}

**Description:** {{description}}

**Evidence:** {{evidence}}

**Gap:** {{gap}}

**Audit Procedure:**

```text
{{audit_procedure}}
```

**Remediation:**

```text
{{remediation}}
```

---
{{/each}}

{{#if no_findings}}
No CIS Docker Benchmark gaps were identified in the reviewed evidence.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Compliance Status

| Status | Count |
|--------|-------|
| Pass | {{count_pass}} |
| Partial | {{count_partial}} |
| Fail | {{count_fail}} |
| Unknown | {{count_unknown}} |
| Not Applicable | {{count_not_applicable}} |

## Review Focus

- Fix failed controls that affect Docker daemon access, socket exposure, privileged containers, host mounts, namespace isolation, and image provenance first.
- Confirm manual controls with operational evidence before marking them as pass.
- Keep raw Docker command output, daemon configuration, and manifest snippets as review evidence.
- Re-run this scan when Docker daemon configuration, image build logic, container runtime flags, or orchestration manifests change.
