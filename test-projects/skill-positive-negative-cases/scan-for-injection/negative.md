# Negative case: scan-for-injection

Expected result: do not invoke `scan-for-injection`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-for-injection`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-for-injection`.

Skill description for comparison:

```text
Scans source code for injection vulnerabilities mapped to OWASP 2025 Injection coverage, including SQL, command, code, NoSQL, LDAP, XXE/XML, and expression language injection.
```
