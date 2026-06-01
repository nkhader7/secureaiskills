# Negative case: scan-json-security

Expected result: do not invoke `scan-json-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-json-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-json-security`.

Skill description for comparison:

```text
Scans JSON configuration, package metadata, policy files, and API fragments for security risks including disabled auth, permissive CORS, plaintext credentials, insecure TLS flags, dependency scripts, and debug exposure.
```
