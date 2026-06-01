# Positive case: audit-auth-session-management

Expected result: invoke `audit-auth-session-management`.

User request:

```text
/audit-auth-session-management D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the audit-auth-session-management workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-auth-session-management\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Audits authentication and session management for password handling, MFA, session cookies, JWT validation, OAuth/OIDC/SAML flows, account recovery, brute force protection, credential stuffing defenses, and authentication failure handling.
- Uses the explicit trigger `/audit-auth-session-management`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js

Expected evidence signals:
- jwt.sign
- expiresIn: '30d'
- secure: false
- sameSite: 'none'

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-auth-session-management\report.md

