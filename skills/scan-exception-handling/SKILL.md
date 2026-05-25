---
name: scan-exception-handling
description: Scans code and configuration for mishandling of exceptional conditions including verbose error disclosure, fail-open authorization, swallowed security exceptions, unsafe retries, missing rollback, crash loops, inconsistent error responses, and exception paths that bypass validation or logging.
triggers:
  - /scan-exception-handling
  - "exception.*handling"
  - "error.*handling"
  - "mishandling.*exception"
  - "fail.*open"
  - "verbose.*error"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-exception-handling

Scans exceptional paths for information leakage, fail-open behavior, and missing recovery or logging.

## Orchestration

1. Load `references/rules.yaml` to get the active `EXC-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/scan-exception-handling
```

Scan a specific path:

```text
/scan-exception-handling src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize exception paths in authentication, authorization, payment, parsing, deserialization, file upload, crypto, and transaction workflows.
