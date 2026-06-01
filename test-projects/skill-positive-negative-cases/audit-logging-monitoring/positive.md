# Positive case: audit-logging-monitoring

Expected result: invoke `audit-logging-monitoring`.

User request:

```text
/audit-logging-monitoring D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the audit-logging-monitoring workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-logging-monitoring\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Audits security logging and alerting controls for missing audit events, weak monitoring, sensitive data in logs, log injection, insufficient retention, tamper-prone logs, and missing detection for authentication, authorization, administrative, and data access events.
- Uses the explicit trigger `/audit-logging-monitoring`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js
- docs/design.md

Expected evidence signals:
- console.log('login failed
- logger.info('password reset token
- No central alerting

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-logging-monitoring\report.md

