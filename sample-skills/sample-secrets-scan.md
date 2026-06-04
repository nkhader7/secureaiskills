---
name: sample-secrets-scan
description: Detects hardcoded API keys, tokens, passwords, and credentials in source code and configuration files
triggers:
  - /sample-secrets-scan
  - "scan.*secrets"
  - "detect.*credentials"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

## Orchestration

You are executing the `sample-secrets-scan` skill. Follow these steps exactly.

### Step 1 — Load Rules and Context

Load the rules from `references/rules.yaml`. Each rule has:
- `id` — unique rule identifier
- `severity` — Critical, High, Medium, Low, or Info
- `patterns` — regex patterns to match against source lines
- `match_strategy` — how to apply patterns (`regex`)
- `remediation` — actionable fix guidance

### Step 2 — Identify Target Files

Run `git diff main...HEAD --name-only` to get changed files.

Skip:
- Binary files
- Lock files (`package-lock.json`, `poetry.lock`, `*.lock`)
- Generated files (`*.min.js`, `dist/`, `build/`)
- `.gitignore` entries

### Step 3 — Evaluate Each File Against Each Rule

For every target file, read its content line by line.
For each rule, apply `match_strategy: regex`:
- Scan each line for the rule's `patterns`
- If a match is found, record a finding

### Step 4 — Redact and Aggregate

For all findings:
- Redact the matched value to `***REDACTED***` before including in the report
- Group findings by severity: Critical → High → Medium → Low → Info

### Step 5 — Render Report

Fill the `report-template.md` placeholders with the aggregated findings.
If no findings exist, show the "No findings" message from the template.

## Usage

Scan changed files (default):
```
/sample-secrets-scan
```

Scan a specific path:
```
/sample-secrets-scan src/config/
```

Scan everything:
```
/sample-secrets-scan --flags=--all
```
