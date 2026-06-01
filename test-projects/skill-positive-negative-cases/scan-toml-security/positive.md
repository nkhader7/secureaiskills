# Positive case: scan-toml-security

Expected result: invoke `scan-toml-security`.

User request:

```text
/scan-toml-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-toml-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-toml-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans TOML configuration files including pyproject, Cargo, service, and application configs for plaintext credentials, disabled TLS, debug mode, wildcard exposure, and unsafe dependency source settings.
- Uses the explicit trigger `/scan-toml-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- config/formats.toml

Expected evidence signals:
- host = "0.0.0.0"
- debug = true
- tls = false
- verify_ssl = false
- api_key = "toml_TEST_SECRET_12345"
- allowed_origins = ["*"]
- url = "http://packages.example.invalid/simple"

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-toml-security\report.md

