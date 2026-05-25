---
name: generate-sbom
description: Generates or reviews software bills of materials for applications, repositories, containers, SBOM files, and release artifacts using SPDX or CycloneDX conventions. Use when the user asks for SBOM generation, dependency inventory, component inventory, package URLs, image SBOMs, license inventory, or release artifact component metadata.
triggers:
  - /generate-sbom
  - "generate.*sbom"
  - "software.*bill.*materials"
  - "cyclonedx"
  - "spdx"
  - "dependency.*inventory"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# generate-sbom

Generates and validates SBOM-ready dependency inventories for applications, containers, and release artifacts.

## Orchestration

1. Load `references/rules.yaml` to get the active `SBOM-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/generate-sbom
```

Scan a specific path:

```text
/generate-sbom src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Prefer CycloneDX or SPDX JSON with package URLs, versions, supplier, licenses, hashes, source path, and container image metadata when available.
