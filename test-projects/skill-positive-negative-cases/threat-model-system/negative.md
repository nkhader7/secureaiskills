# Negative case: threat-model-system

Expected result: do not invoke `threat-model-system`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/threat-model-system`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `threat-model-system`.

Skill description for comparison:

```text
Builds a lightweight system threat model from product, architecture, API, data-flow, and infrastructure context. Use during design review or when a feature changes trust boundaries, authentication, authorization, sensitive data handling, external integrations, or deployment architecture.
```
