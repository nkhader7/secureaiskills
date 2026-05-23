---
name: scan-for-injection
description: Scans code for injection vulnerabilities including SQL injection, XSS, weak cryptography, and missing authorization checks
triggers:
  - /scan-for-injection
  - "scan.*injection"
  - "detect.*injection"
  - "find.*xss"
  - "check.*sql.*injection"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# scan-for-injection

Scans source code for injection vulnerabilities and related code-level risks: SQL injection, cross-site scripting, weak cryptographic algorithms, missing authorization checks, and unsafe configuration patterns.

For hardcoded secrets and credentials, use `detect-secrets` instead.

## Orchestration

1. Load `references/rules.yaml` to get the active rule set.
2. Identify changed files on the current branch (`git diff main...HEAD --name-only`).
3. For each changed file, evaluate every line against each rule's `patterns`.
4. Aggregate findings by severity (Critical → High → Medium → Low → Info).
5. Render the final report using `references/report-template.md`.

## Usage

Scan changed files on the current branch:

```
/scan-for-injection
```

Scan a specific path:

```
/scan-for-injection src/api/
```
