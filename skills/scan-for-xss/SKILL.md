---
name: scan-for-xss
description: Scans frontend and backend code for cross-site scripting risks including reflected XSS, stored XSS, DOM XSS, unsafe HTML sinks, unsafe template rendering, missing output encoding, sanitizer misuse, unsafe markdown rendering, and weak Content Security Policy.
triggers:
  - /scan-for-xss
  - "scan.*xss"
  - "cross.*site.*scripting"
  - "dom.*xss"
  - "unsafe.*innerHTML"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-for-xss

Scans code and templates for reflected, stored, and DOM-based XSS risks.

## Orchestration

1. Load `references/rules.yaml` to get the active `XSS-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/scan-for-xss
```

Scan a specific path:

```text
/scan-for-xss src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize user-controlled data flowing into HTML, JavaScript, URL, CSS, markdown, rich text, and template sinks.
