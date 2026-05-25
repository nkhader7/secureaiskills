---
name: audit-auth-session-management
description: Audits authentication and session management for password handling, MFA, session cookies, JWT validation, OAuth/OIDC/SAML flows, account recovery, brute force protection, credential stuffing defenses, and authentication failure handling.
triggers:
  - /audit-auth-session-management
  - "audit.*auth"
  - "session.*management"
  - "jwt.*security"
  - "oauth.*security"
  - "mfa"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# audit-auth-session-management

Audits authentication and session controls for account compromise and session takeover risks.

## Orchestration

1. Load `references/rules.yaml` to get the active `ASM-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/audit-auth-session-management
```

Scan a specific path:

```text
/audit-auth-session-management src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prioritize credential handling, MFA bypass, weak session cookies, JWT verification, OAuth redirect handling, and recovery flows.
