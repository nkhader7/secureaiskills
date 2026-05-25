---
name: scan-broken-access-control
description: Scans applications, APIs, services, policies, and tests for broken access control risks such as missing authorization checks, IDOR/BOLA, privilege escalation, tenant isolation failures, unsafe CORS, path traversal, and overbroad object access.
triggers:
  - /scan-broken-access-control
  - "scan.*broken.*access"
  - "access.*control"
  - "idor"
  - "bola"
  - "authorization.*bypass"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-broken-access-control

Scans for authorization and privilege-boundary failures across applications and APIs.

## Orchestration

1. Load `references/rules.yaml` to get the active `BAC-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/scan-broken-access-control
```

Scan a specific path:

```text
/scan-broken-access-control src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize object-level authorization, tenant isolation, admin-only operations, and state-changing routes that depend only on client-controlled identifiers.
