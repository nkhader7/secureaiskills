---
name: audit-crypto-usage
description: Audits code and configuration for cryptographic failures including weak algorithms, insecure random number generation, poor key management, unsafe TLS, missing encryption, weak password hashing, hardcoded keys, and misuse of crypto APIs.
triggers:
  - /audit-crypto-usage
  - "audit.*crypto"
  - "cryptographic.*failure"
  - "weak.*cipher"
  - "key.*management"
  - "password.*hash"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# audit-crypto-usage

Audits cryptographic code and configuration for algorithm, key, TLS, and storage failures.

## Orchestration

1. Load `references/rules.yaml` to get the active `ACU-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/audit-crypto-usage
```

Scan a specific path:

```text
/audit-crypto-usage src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize hardcoded keys, broken algorithms, unsafe randomness, TLS verification bypass, and password hashing mistakes.
