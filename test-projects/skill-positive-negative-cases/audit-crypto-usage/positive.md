# Positive case: audit-crypto-usage

Expected result: invoke `audit-crypto-usage`.

User request:

```text
/audit-crypto-usage D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the audit-crypto-usage workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-crypto-usage\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Audits code and configuration for cryptographic failures including weak algorithms, insecure random number generation, poor key management, unsafe TLS, missing encryption, weak password hashing, hardcoded keys, and misuse of crypto APIs.
- Uses the explicit trigger `/audit-crypto-usage`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js

Expected evidence signals:
- md5
- Math.random
- rejectUnauthorized: false

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-crypto-usage\report.md

