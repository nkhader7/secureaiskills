# Negative case: generate-dependency-graph

Expected result: do not invoke `generate-dependency-graph`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/generate-dependency-graph`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `generate-dependency-graph`.

Skill description for comparison:

```text
Generates dependency graphs for applications, repositories, containers, and SBOMs, including direct and transitive package relationships, dependency paths, parent chains, ownership hints, vulnerable package impact paths, and call graph or reachability evidence when available.
```
