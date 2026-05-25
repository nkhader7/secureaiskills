# scan-kubernetes-manifests Report

| Field | Value |
|-------|-------|
| Skill | scan-kubernetes-manifests |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Benchmark | CIS Kubernetes-style controls |
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
No Kubernetes benchmark gaps were identified in the reviewed evidence.
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

- Fix failed controls that affect API server authentication, authorization, audit logging, TLS, etcd, kubelet authorization, privileged pods, host namespace sharing, hostPath mounts, RBAC, and secrets first.
- Confirm manual controls with operational evidence before marking them as pass.
- Keep raw `kubectl`, process-list, static pod, kubelet, and audit-policy evidence with the review.
- Re-run this scan when Kubernetes manifests, cluster bootstrap configuration, admission policy, RBAC, network policy, or workload security contexts change.
