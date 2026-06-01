# Negative case: generate-sbom

Expected result: do not invoke `generate-sbom`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/generate-sbom`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `generate-sbom`.

Skill description for comparison:

```text
Generates or reviews software bills of materials for applications, repositories, containers, SBOM files, and release artifacts using SPDX or CycloneDX conventions. Use when the user asks for SBOM generation, dependency inventory, component inventory, package URLs, image SBOMs, license inventory, or release artifact component metadata.
```
