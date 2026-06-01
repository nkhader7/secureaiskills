# Positive case: scan-yaml-security

Expected result: invoke `scan-yaml-security`.

User request:

```text
/scan-yaml-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-yaml-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-yaml-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans YAML and YML configuration files for security risks including disabled authentication, wildcard exposure, plaintext secrets, insecure TLS flags, privileged workload settings, and unsafe deserialization hints.
- Uses the explicit trigger `/scan-yaml-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- config/formats.yaml

Expected evidence signals:
- auth: false
- host: "0.0.0.0"
- allowedOrigins: ["*"]
- tls: false
- api_key: "yaml_TEST_SECRET_12345"
- privileged: true
- runAsUser: 0

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-yaml-security\report.md

