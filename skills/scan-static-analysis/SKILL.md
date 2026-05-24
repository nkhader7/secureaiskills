---
name: scan-static-analysis
description: Runs or plans static analysis using CodeQL, Semgrep, and SARIF processing. Use when scanning a workspace for vulnerabilities, selecting CodeQL or Semgrep rulesets, generating a SAST scan plan, processing SARIF results, or combining static-analysis findings from multiple tools.
triggers:
  - /scan-static-analysis
  - "static.*analysis"
  - "run.*sast"
  - "codeql.*scan"
  - "semgrep.*scan"
  - "parse.*sarif"
  - "process.*sarif"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# scan-static-analysis

Plans and runs static-analysis workflows using CodeQL, Semgrep, and SARIF result processing.

## Orchestration

1. Load `references/rules.yaml` to get the active static-analysis ruleset catalog.
2. Identify the target:
   - Default to the current workspace.
   - Use a user-provided file, directory, repository checkout, CodeQL database, or SARIF file when supplied.
3. Classify the request:
   - Use CodeQL for deep interprocedural data-flow and taint analysis.
   - Use Semgrep for fast pattern-based and taint-mode scanning.
   - Use SARIF processing when results already exist.
4. Detect languages, frameworks, infrastructure files, and existing scanner outputs.
5. Select rules from `references/rules.yaml`:
   - Include baseline security rules.
   - Add language and framework-specific rulesets.
   - Add infrastructure rulesets when IaC, containers, CI/CD, or policy files are present.
   - Include required third-party rulesets when language coverage matches.
   - Choose CodeQL threat-model inputs that match the application boundary.
6. Present the scan plan before running tools:
   - Target path.
   - Tooling selected.
   - Mode: `important-only` or `run-all`.
   - Rulesets and third-party sources.
   - Output directory.
7. Run approved scans or parse approved SARIF files.
8. Normalize, aggregate, deduplicate, and prioritize findings.
9. Render the final report using `references/report-template.md`.

## Usage

Plan a static-analysis scan for the current workspace:

```text
/scan-static-analysis
```

Run a Semgrep-focused scan:

```text
/scan-static-analysis --tool semgrep --mode important-only
```

Run a CodeQL-focused scan:

```text
/scan-static-analysis --tool codeql --mode run-all
```

Parse existing SARIF:

```text
/scan-static-analysis --sarif static_analysis/results/results.sarif
```

## Review Guidance

Prefer `important-only` for pull requests and CI-style blocking checks. Prefer `run-all` for manual audits, variant hunting, and research. Treat zero findings as inconclusive until tool installation, database quality, selected rulesets, and SARIF validity have been checked.
