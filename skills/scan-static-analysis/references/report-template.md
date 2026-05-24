# scan-static-analysis Report

| Field | Value |
|-------|-------|
| Skill | scan-static-analysis |
| Target | {{target}} |
| Date | {{date}} |
| Branch | {{branch}} |
| Tools | {{tools}} |
| Mode | {{mode}} |
| Rulesets | {{rulesets}} |
| Files Reviewed | {{file_count}} |
| Total Findings | {{total_findings}} |
| Overall Severity | {{overall_severity}} |

---

## Scan Plan

**Target:** {{target}}

**Output Directory:** {{output_directory}}

**Tooling:** {{tools}}

**Selected Rules:** {{selected_rules}}

**Excluded Rules:** {{excluded_rules}}

**Reasoning:** {{selection_reasoning}}

## Findings

{{#each findings}}
### [{{severity}}] {{rule_id}} - {{rule_name}}

**Tool:** {{tool}}
**File:** `{{file}}` (line {{line}})
**Category:** {{category}}
**Message:** {{message}}
**Confidence:** {{confidence}}
**Impact:** {{impact}}

```text
{{snippet}}
```

**Remediation:** {{remediation}}

---
{{/each}}

{{#if no_findings}}
No static-analysis findings were reported by the selected tools and rulesets.
{{/if}}

## Summary Table

| Severity | Count |
|----------|-------|
| Critical | {{count_critical}} |
| High     | {{count_high}} |
| Medium   | {{count_medium}} |
| Low      | {{count_low}} |
| Info     | {{count_info}} |

## Tool Quality Checks

- CodeQL database quality: {{codeql_database_quality}}
- Semgrep engine mode: {{semgrep_engine_mode}}
- SARIF validation: {{sarif_validation}}
- Zero-finding review: {{zero_finding_review}}

## Next Steps

- Address **Critical** and **High** findings before merging.
- Review **Medium** findings and document accepted risk.
- Re-run with `run-all` mode for manual audit coverage when time permits.
- Preserve raw SARIF output for baselining, deduplication, and regression checks.
