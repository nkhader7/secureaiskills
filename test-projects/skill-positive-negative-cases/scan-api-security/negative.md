# Negative case: scan-api-security

Expected result: do not invoke `scan-api-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-api-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-api-security`.

Skill description for comparison:

```text
Scans API implementations, gateway configs, and OpenAPI definitions for common API security risks aligned to OWASP API Security Top 10 2023.
```
