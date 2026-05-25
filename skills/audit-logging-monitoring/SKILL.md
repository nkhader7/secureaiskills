---
name: audit-logging-monitoring
description: Audits security logging and alerting controls for missing audit events, weak monitoring, sensitive data in logs, log injection, insufficient retention, tamper-prone logs, and missing detection for authentication, authorization, administrative, and data access events.
triggers:
  - /audit-logging-monitoring
  - "audit.*logging"
  - "security.*logging"
  - "alerting.*failure"
  - "monitoring.*gap"
  - "audit.*trail"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# audit-logging-monitoring

Audits whether security-relevant events are recorded, protected, monitored, and actionable.

## Orchestration

1. Load `references/rules.yaml` to get the active `ALM-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/audit-logging-monitoring
```

Scan a specific path:

```text
/audit-logging-monitoring src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize authentication, authorization, admin, secret, data access, payment, and release events that lack logs or alerts.
