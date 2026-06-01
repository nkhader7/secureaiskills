# Negative case: detect-supply-chain-risks

Expected result: do not invoke `detect-supply-chain-risks`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/detect-supply-chain-risks`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `detect-supply-chain-risks`.

Skill description for comparison:

```text
Detects software supply chain risks across repositories, dependency manifests, package registries, CI/CD workflows, container references, release artifacts, build scripts, and provenance evidence. Use when reviewing dependency confusion, typosquatting, unpinned GitHub Actions, mutable image tags, unsigned artifacts, missing SBOM/provenance, unsafe package install scripts, weak CI permissions, registry trust, or software/data integrity failures.
```
