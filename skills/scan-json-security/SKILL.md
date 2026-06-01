---
name: scan-json-security
description: Scans JSON configuration, package metadata, policy files, and API fragments for security risks including disabled auth, permissive CORS, plaintext credentials, insecure TLS flags, dependency scripts, and debug exposure.
triggers:
  - /scan-json-security
  - "scan.*json.*security"
  - "review.*json.*config"
  - "check.*json.*secrets"
  - "audit.*package.*json"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-json-security

Scan JSON files for security-sensitive values, unsafe defaults, and executable package metadata.

## Orchestration

1. Load `references/rules.yaml` to get the active `JSON-` rule set.
2. Include `*.json` files from user-supplied paths or changed files.
3. Skip large lock files unless dependency or supply-chain review is explicitly requested.
4. Preserve object-path context when possible, such as `security.enabled` or `scripts.postinstall`.
5. Evaluate each rule using its `match_strategy`, capturing file, line, snippet, and confidence.
6. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable`.
7. Render the final report using `references/report-template.md`.

## Usage

Scan JSON files in the current change:

```text
/scan-json-security
```

Scan a specific JSON config:

```text
/scan-json-security config/app.json package.json
```

## Review Guidance

Focus on security toggles, credential-like values, CORS origins, TLS validation flags, debug settings, and executable dependency lifecycle scripts.
