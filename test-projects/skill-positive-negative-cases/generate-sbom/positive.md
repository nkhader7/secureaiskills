# Positive case: generate-sbom

Expected result: invoke `generate-sbom`.

User request:

```text
/generate-sbom D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the generate-sbom workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\generate-sbom\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Generates or reviews software bills of materials for applications, repositories, containers, SBOM files, and release artifacts using SPDX or CycloneDX conventions. Use when the user asks for SBOM generation, dependency inventory, component inventory, package URLs, image SBOMs, license inventory, or release artifact component metadata.
- Uses the explicit trigger `/generate-sbom`.
- Points at known fixture evidence for this skill.

Fixture targets:
- sbom/cyclonedx.json
- package.json

Expected evidence signals:
- bomFormat
- CycloneDX
- components

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\generate-sbom\report.md

