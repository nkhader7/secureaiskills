---
name: scan-toml-security
description: Scans TOML configuration files including pyproject, Cargo, service, and application configs for plaintext credentials, disabled TLS, debug mode, wildcard exposure, and unsafe dependency source settings.
triggers:
  - /scan-toml-security
  - "scan.*toml.*security"
  - "review.*toml.*config"
  - "check.*pyproject.*security"
  - "audit.*cargo.*config"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-toml-security

Scan TOML files for insecure configuration values, dependency-source risks, and plaintext credentials.

## Orchestration

1. Load `references/rules.yaml` to get the active `TOML-` rule set.
2. Include `*.toml` files from user-supplied paths or changed files.
3. Preserve table context when possible, such as `[server]` or `[tool.poetry.source]`.
4. Evaluate each rule using its `match_strategy`, capturing file, line, snippet, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable`.
6. Render the final report using `references/report-template.md`.

## Usage

Scan TOML files in the current change:

```text
/scan-toml-security
```

Scan a specific TOML config:

```text
/scan-toml-security pyproject.toml config/
```

## Review Guidance

Focus on credentials, TLS verification, debug mode, wildcard listeners, and package index/source settings that could affect supply-chain trust.
