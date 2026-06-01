# Positive case: scan-broken-access-control

Expected result: invoke `scan-broken-access-control`.

User request:

```text
/scan-broken-access-control D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-broken-access-control workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-broken-access-control\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans applications, APIs, services, policies, and tests for broken access control risks such as missing authorization checks, IDOR/BOLA, privilege escalation, tenant isolation failures, unsafe CORS, path traversal, and overbroad object access.
- Uses the explicit trigger `/scan-broken-access-control`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js
- api/openapi.yaml

Expected evidence signals:
- req.params.id
- SELECT * FROM users WHERE id
- cors({ origin: '*'

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-broken-access-control\report.md

