# Negative case: audit-logging-monitoring

Expected result: do not invoke `audit-logging-monitoring`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/audit-logging-monitoring`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `audit-logging-monitoring`.

Skill description for comparison:

```text
Audits security logging and alerting controls for missing audit events, weak monitoring, sensitive data in logs, log injection, insufficient retention, tamper-prone logs, and missing detection for authentication, authorization, administrative, and data access events.
```
