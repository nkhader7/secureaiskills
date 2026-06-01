# Positive case: generate-dependency-graph

Expected result: invoke `generate-dependency-graph`.

User request:

```text
/generate-dependency-graph D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the generate-dependency-graph workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\generate-dependency-graph\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Generates dependency graphs for applications, repositories, containers, and SBOMs, including direct and transitive package relationships, dependency paths, parent chains, ownership hints, vulnerable package impact paths, and call graph or reachability evidence when available.
- Uses the explicit trigger `/generate-dependency-graph`.
- Points at known fixture evidence for this skill.

Fixture targets:
- sbom/cyclonedx.json
- package-lock.json

Expected evidence signals:
- dependsOn
- lodash
- minimist

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\generate-dependency-graph\report.md

