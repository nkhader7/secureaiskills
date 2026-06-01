# Negative case: scan-yaml-security

Expected result: do not invoke `scan-yaml-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-yaml-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-yaml-security`.

Skill description for comparison:

```text
Scans YAML and YML configuration files for security risks including disabled authentication, wildcard exposure, plaintext secrets, insecure TLS flags, privileged workload settings, and unsafe deserialization hints.
```
