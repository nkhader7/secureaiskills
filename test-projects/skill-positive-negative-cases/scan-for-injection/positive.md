# Positive case: scan-for-injection

Expected result: invoke `scan-for-injection`.

User request:

```text
/scan-for-injection D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-for-injection workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-injection\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans source code for injection vulnerabilities mapped to OWASP 2025 Injection coverage, including SQL, command, code, NoSQL, LDAP, XXE/XML, and expression language injection.
- Uses the explicit trigger `/scan-for-injection`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js

Expected evidence signals:
- SELECT * FROM users WHERE id = ' + req.params.id
- exec('convert ' + req.query.file
- eval(req.body.expression)

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-injection\report.md

