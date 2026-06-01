# Positive case: threat-model-system

Expected result: invoke `threat-model-system`.

User request:

```text
/threat-model-system D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the threat-model-system workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\threat-model-system\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Builds a lightweight system threat model from product, architecture, API, data-flow, and infrastructure context. Use during design review or when a feature changes trust boundaries, authentication, authorization, sensitive data handling, external integrations, or deployment architecture.
- Uses the explicit trigger `/threat-model-system`.
- Points at known fixture evidence for this skill.

Fixture targets:
- docs/design.md

Expected evidence signals:
- Trust boundaries are TBD
- No abuse cases
- No documented data classification

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\threat-model-system\report.md

