# Positive case: scan-sca-dependencies

Expected result: invoke `scan-sca-dependencies`.

User request:

```text
/scan-sca-dependencies D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-sca-dependencies workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-sca-dependencies\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Detects vulnerable third-party packages and evaluates OWASP OSS Top 10 risks across application dependency manifests, lockfiles, SBOMs, container images, OS package inventories, and build artifacts. Use when the user asks to find vulnerable packages, vulnerable dependencies, CVEs, package versions, severity, fixed versions, SCA findings, image vulnerabilities, dependency vulnerability reports, unmaintained packages, license risk, name confusion attacks, or supply chain integrity gaps.
- Uses the explicit trigger `/scan-sca-dependencies`.
- Points at known fixture evidence for this skill.

Fixture targets:
- package.json
- package-lock.json
- sbom/cyclonedx.json

Expected evidence signals:
- lodash
- 4.17.20
- CVE-2021-23337

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-sca-dependencies\report.md

