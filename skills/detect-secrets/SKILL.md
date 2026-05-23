---
name: detect-secrets
description: Detects hardcoded secrets, credentials, and sensitive tokens committed to source code
triggers:
  - /detect-secrets
  - "detect.*secret"
  - "secret.*detect"
  - "find.*credential"
  - "scan.*token"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# detect-secrets

Detects hardcoded secrets, API keys, private keys, tokens, and credentials that should never appear in source code.

## Orchestration

1. Load `references/rules.yaml` to get the active rule set.
2. Identify files to scan — default to changed files on the current branch (`git diff main...HEAD --name-only`); scan all tracked files when a path argument is provided.
3. Skip binary files, lock files (`package-lock.json`, `*.lock`), and files listed in `.gitignore`.
4. For each file, evaluate every line against each rule's `patterns`.
5. For each match, capture the file path, line number, rule ID, and a masked snippet (replace the matched secret value with `***REDACTED***`).
6. Aggregate findings by severity (Critical → High → Medium → Low → Info).
7. Render the final report using `references/report-template.md`.

## Usage

Scan changed files on the current branch:

```
/detect-secrets
```

Scan a specific path or directory:

```
/detect-secrets src/config/
```

Scan all tracked files in the repository:

```
/detect-secrets --all
```
