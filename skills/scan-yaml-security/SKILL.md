---
name: scan-yaml-security
description: Scans YAML and YML configuration files for security risks including disabled authentication, wildcard exposure, plaintext secrets, insecure TLS flags, privileged workload settings, and unsafe deserialization hints.
triggers:
  - /scan-yaml-security
  - "scan.*yaml.*security"
  - "scan.*yml.*security"
  - "review.*yaml.*config"
  - "check.*yaml.*secrets"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-yaml-security

Scan YAML configuration files for security-sensitive settings and risky defaults.

## Orchestration

1. Load `references/rules.yaml` to get the active `YAML-` rule set.
2. Include `*.yaml` and `*.yml` files from user-supplied paths or changed files.
3. Skip generated dependency lock files unless the request explicitly targets them.
4. Preserve YAML path context when reporting a finding, such as `auth.enabled` or `containers[0].securityContext`.
5. Evaluate each rule using its `match_strategy`, capturing file, line, snippet, and confidence.
6. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
7. Render the final report using `references/report-template.md`.

## Usage

Scan YAML files in the current change:

```text
/scan-yaml-security
```

Scan a specific configuration folder:

```text
/scan-yaml-security config/ deploy/
```

## Review Guidance

Treat YAML as executable configuration. Prioritize settings that affect authentication, network exposure, TLS validation, container privileges, and secret material.
