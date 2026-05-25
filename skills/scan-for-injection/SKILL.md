---
name: scan-for-injection
description: Scans source code for injection vulnerabilities mapped to OWASP 2025 Injection coverage, including SQL, command, code, NoSQL, LDAP, XXE/XML, and expression language injection.
triggers:
  - /scan-for-injection
  - "scan.*injection"
  - "detect.*injection"
  - "check.*sql.*injection"
  - "check.*command.*injection"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-for-injection

Scans source code for injection vulnerabilities: SQL injection, command injection, code injection, NoSQL injection, LDAP injection, XXE/XML injection, and expression language injection.

For hardcoded secrets and credentials, use `detect-secrets` instead.

## Orchestration

1. Load `references/rules.yaml` to get the active rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify changed files on the current branch with `git diff main...HEAD --name-only`.
4. For each changed file, evaluate every line or local code block against each rule's `patterns`.
5. Include OWASP 2025, CWE, and CAPEC metadata in any finding when present.
6. Aggregate findings by severity: Critical, High, Medium, Low, Info.
7. Render the final report using `references/report-template.md`.

## Usage

Scan changed files on the current branch:

```text
/scan-for-injection
```

Scan a specific path:

```text
/scan-for-injection src/api/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.
