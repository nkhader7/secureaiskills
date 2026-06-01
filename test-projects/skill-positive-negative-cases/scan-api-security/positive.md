# Positive case: scan-api-security

Expected result: invoke `scan-api-security`.

User request:

```text
/scan-api-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-api-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-api-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans API implementations, gateway configs, and OpenAPI definitions for common API security risks aligned to OWASP API Security Top 10 2023.
- Uses the explicit trigger `/scan-api-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- api/openapi.yaml
- src/app.js

Expected evidence signals:
- security: []
- /admin/users/{id}
- x-tenant-id

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-api-security\report.md

