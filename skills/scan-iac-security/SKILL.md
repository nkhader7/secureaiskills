---
name: scan-iac-security
description: Scans infrastructure-as-code changes for security misconfigurations in Terraform, CloudFormation, ARM/Bicep, Pulumi config, and related IaC files.
triggers:
  - /scan-iac-security
  - "scan.*iac"
  - "iac.*security"
  - "check.*terraform"
  - "scan.*infrastructure"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# scan-iac-security

Scan infrastructure-as-code for security misconfigurations before deployment.

## Orchestration

1. Load `references/rules.yaml` to get the active IaC rule set.
2. Identify target files:
   - Default to changed files on the current branch with `git diff main...HEAD --name-only`.
   - Include only IaC files such as `*.tf`, `*.tfvars`, `*.hcl`, `*.yaml`, `*.yml`, `*.json`, `*.bicep`, `*.template`, and Pulumi config files.
   - Scan a user-provided path when one is supplied.
3. Skip binary files, generated files, lock files, vendored modules, `.terraform/`, `node_modules/`, and build output directories.
4. Evaluate each file against every rule in `references/rules.yaml`.
   - For `match_strategy: regex`, report a finding when one pattern matches the target file or resource block.
   - For resource-context rules, report a finding only when the risky attributes appear in the same resource, policy statement, ingress rule, or configuration block.
   - For `match_strategy: checkov_graph_check`, interpret `implementation.code` as a Checkov-style graph policy definition and evaluate the resource attributes, resource types, connections, and operators described by that policy.
   - For `match_strategy: synthesized_checkov_python`, evaluate the rule against matching `frameworks` and `resource_types` using `detection.requirement`, `detection.signals`, and `detection.logic_hints`.
5. Capture file path, line number, rule ID, matched snippet, and surrounding resource context when possible.
6. Aggregate findings by severity: Critical, High, Medium, Low, Info.
7. Render the final report using `references/report-template.md`.

## Usage

Scan changed IaC files on the current branch:

```text
/scan-iac-security
```

Scan a specific path:

```text
/scan-iac-security infrastructure/
```

Scan Terraform only:

```text
/scan-iac-security infra/terraform/
```

## Review Guidance

Prioritize findings that expose public access, disable encryption, grant wildcard permissions, or weaken network boundaries. Treat generated IaC as lower signal unless the generated source cannot be reviewed. Imported and synthesized Checkov policies should be treated as detection criteria; preserve the rule ID in the report.
