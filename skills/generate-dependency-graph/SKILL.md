---
name: generate-dependency-graph
description: Generates dependency graphs for applications, repositories, containers, and SBOMs, including direct and transitive package relationships, dependency paths, parent chains, ownership hints, vulnerable package impact paths, and call graph or reachability evidence when available.
triggers:
  - /generate-dependency-graph
  - "dependency.*graph"
  - "transitive.*dependency"
  - "dependency.*path"
  - "call.*graph"
  - "reachability.*analysis"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# generate-dependency-graph

Generates direct/transitive dependency maps and impact paths for packages, images, and SBOMs.

## Orchestration

1. Load `references/rules.yaml` to get the active `DG-` rule set.
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify target evidence from source code, configuration, tests, API specs, IaC, CI/CD, runtime manifests, and documentation relevant to the request.
4. Evaluate each rule using its `match_strategy`, preserving file path, line, snippet, control context, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable` based on available evidence.
6. Prioritize findings by severity, exploitability, exposed surface, and whether a concrete remediation is available.
7. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/generate-dependency-graph
```

Scan a specific path:

```text
/generate-dependency-graph src/ services/ docs/
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

Use this when the user needs graph visualization, parent paths, impact tracing, ownership mapping, or reachability analysis beyond SCA CVE reporting.
