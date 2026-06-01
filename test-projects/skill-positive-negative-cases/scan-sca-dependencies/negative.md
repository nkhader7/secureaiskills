# Negative case: scan-sca-dependencies

Expected result: do not invoke `scan-sca-dependencies`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-sca-dependencies`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-sca-dependencies`.

Skill description for comparison:

```text
Detects vulnerable third-party packages and evaluates OWASP OSS Top 10 risks across application dependency manifests, lockfiles, SBOMs, container images, OS package inventories, and build artifacts. Use when the user asks to find vulnerable packages, vulnerable dependencies, CVEs, package versions, severity, fixed versions, SCA findings, image vulnerabilities, dependency vulnerability reports, unmaintained packages, license risk, name confusion attacks, or supply chain integrity gaps.
```
