# Negative case: audit-auth-session-management

Expected result: do not invoke `audit-auth-session-management`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/audit-auth-session-management`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `audit-auth-session-management`.

Skill description for comparison:

```text
Audits authentication and session management for password handling, MFA, session cookies, JWT validation, OAuth/OIDC/SAML flows, account recovery, brute force protection, credential stuffing defenses, and authentication failure handling.
```
