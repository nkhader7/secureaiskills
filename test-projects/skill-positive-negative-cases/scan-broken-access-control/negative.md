# Negative case: scan-broken-access-control

Expected result: do not invoke `scan-broken-access-control`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-broken-access-control`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-broken-access-control`.

Skill description for comparison:

```text
Scans applications, APIs, services, policies, and tests for broken access control risks such as missing authorization checks, IDOR/BOLA, privilege escalation, tenant isolation failures, unsafe CORS, path traversal, and overbroad object access.
```
