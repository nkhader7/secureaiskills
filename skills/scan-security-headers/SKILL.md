---
name: scan-security-headers
description: Scans web applications, APIs, reverse proxies, CDN configuration, and middleware for missing or unsafe HTTP security headers, cookie flags, CORS policy, CSP, HSTS, clickjacking protections, MIME sniffing protections, referrer policy, and browser-facing misconfiguration.
triggers:
  - /scan-security-headers
  - "security.*headers"
  - "http.*headers"
  - "csp"
  - "hsts"
  - "cors.*header"
  - "cookie.*flags"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-security-headers

Scans browser-facing HTTP response hardening controls.

## Orchestration

1. Load `references/rules.yaml` to get the active `SHD-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/scan-security-headers
```

Scan a specific path:

```text
/scan-security-headers src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize production routes, authenticated pages, admin surfaces, OAuth redirects, file downloads, and any response that handles sensitive data.
