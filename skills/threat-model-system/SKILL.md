---
name: threat-model-system
description: Builds a lightweight system threat model from product, architecture, API, data-flow, and infrastructure context. Use during design review or when a feature changes trust boundaries, authentication, authorization, sensitive data handling, external integrations, or deployment architecture.
triggers:
  - /threat-model-system
  - "threat.*model"
  - "model.*threat"
  - "security.*design.*review"
  - "review.*architecture.*risk"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# threat-model-system

Creates a structured threat model for the code and design artifacts in the current workspace.

## Orchestration

1. Load `references/rules.yaml` to get the active threat-modeling criteria.
2. Gather available system context from user input and repository artifacts:
   - Design docs, README files, ADRs, API specs, diagrams, data schemas, IaC, service configs, auth code, routing code, and deployment notes.
   - Prefer changed files on the current branch when reviewing a pull request or feature branch.
   - Scan a user-provided path when one is supplied.
3. Identify core model elements:
   - Assets and sensitive data.
   - Actors and identities.
   - Entry points and exposed interfaces.
   - Trust boundaries.
   - Data flows and storage locations.
   - External dependencies and third-party integrations.
   - Privileged operations and administrative paths.
4. Evaluate the system against every rule in `references/rules.yaml`.
   - For `match_strategy: design_review`, use the rule as a review question and evidence checklist.
   - Report a finding when required controls are missing, ambiguous, unverifiable, or contradicted by available evidence.
   - Mark unknowns as findings when the missing information blocks a security decision.
5. For each finding, capture the affected component, rule ID, threat scenario, evidence, impact, likelihood, and recommended mitigation.
6. Aggregate findings by severity: Critical, High, Medium, Low, Info.
7. Render the final threat model using `references/report-template.md`.

## Usage

Threat model a feature or design from the current context:

```text
/threat-model-system
```

Threat model a specific directory or document:

```text
/threat-model-system docs/checkout-design.md
```

Threat model changed architecture and code on the current branch:

```text
/threat-model-system --changed
```

## Review Guidance

Prioritize threats that cross trust boundaries, expose sensitive data, weaken authentication or authorization, introduce unsafe defaults, or rely on unclear ownership. Treat missing design evidence as a real risk when it prevents validation of critical controls.
