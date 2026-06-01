# Positive case: detect-secrets

Expected result: invoke `detect-secrets`.

User request:

```text
/detect-secrets D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the detect-secrets workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\detect-secrets\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Detects hardcoded secrets, credentials, and sensitive tokens committed to source code
- Uses the explicit trigger `/detect-secrets`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js
- .env.example

Expected evidence signals:
- AWS_ACCESS_KEY_ID_EXAMPLE
- -----BEGIN RSA PRIVATE KEY-----
- AZURE_CLIENT_SECRET

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\detect-secrets\report.md

