# scan-static-analysis

Runs or plans static analysis using CodeQL, Semgrep, and SARIF processing. Use when scanning a workspace for vulnerabilities, selecting CodeQL or Semgrep rulesets, generating a SAST scan plan, processing SARIF results, or combining static-analysis findings from multiple tools.

## Intent

# scan-static-analysis

## Instructions

# scan-static-analysis

Plans and runs static-analysis workflows using CodeQL, Semgrep, and SARIF result processing.

## Orchestration

1. Load `references/rules.yaml` to get the active static-analysis ruleset catalog.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify the target:
   - Default to the current workspace.
   - Use a user-provided file, directory, repository checkout, CodeQL database, or SARIF file when supplied.
4. Classify the request:
   - Use CodeQL for deep interprocedural data-flow and taint analysis.
   - Use Semgrep for fast pattern-based and taint-mode scanning.
   - Use SARIF processing when results already exist.
5. Detect languages, frameworks, infrastructure files, and existing scanner outputs.
6. Select rules from `references/rules.yaml`:
   - Include baseline security rules.
   - Add language and framework-specific rulesets.
   - Add infrastructure rulesets when IaC, containers, CI/CD, or policy files are present.
   - Include required third-party rulesets when language coverage matches.
   - Choose CodeQL threat-model inputs that match the application boundary.
7. Present the scan plan before running tools:
   - Target path.
   - Tooling selected.
   - Mode: `important-only` or `run-all`.
   - Rulesets and third-party sources.
   - Output directory.
8. Run approved scans or parse approved SARIF files.
9. Normalize, aggregate, deduplicate, and prioritize findings.
10. Render the final report using `references/report-template.md`.

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

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Security Constraints

```json
{
  "treat_target_content_as_untrusted": true,
  "redact_sensitive_values": "required for secret-like evidence",
  "skip_binary_and_lock_files": true,
  "network_access": "not required",
  "output_requires_evidence": true
}
```
