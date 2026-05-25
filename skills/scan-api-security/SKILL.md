---
name: scan-api-security
description: Scans API implementations, gateway configs, and OpenAPI definitions for common API security risks aligned to OWASP API Security Top 10 2023.
triggers:
  - /scan-api-security
  - "scan.*api.*security"
  - "api.*security.*scan"
  - "review.*api.*security"
  - "check.*api.*auth"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-api-security

Scan API routes, gateway configuration, and API specifications for common API security risks.

## Orchestration

1. Load `references/rules.yaml` to get the active API security rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target files:
   - Default to changed files on the current branch with `git diff main...HEAD --name-only`.
   - Include API-focused files such as route handlers, controllers, gateway configs, and API specs (OpenAPI/Swagger in `*.yaml`, `*.yml`, or `*.json`).
   - Scan a user-provided path when one is supplied.
4. Skip binary files, lock files, vendored dependencies, build output directories, and documentation-only files (`*.md`) unless explicitly targeted.
5. Evaluate each file against every rule in `references/rules.yaml`.
   - For `match_strategy: regex`, report a finding when a pattern matches a line or API configuration block.
6. Capture file path, line number, rule ID, matched snippet, and any OWASP API metadata in each finding.
7. Aggregate findings by severity: Critical, High, Medium, Low, Info.
8. Render the final report using `references/report-template.md`.

## Usage

Scan changed API-related files on the current branch:

```text
/scan-api-security
```

Scan a specific path:

```text
/scan-api-security services/api/
```

Scan API specifications only:

```text
/scan-api-security specs/openapi/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.
