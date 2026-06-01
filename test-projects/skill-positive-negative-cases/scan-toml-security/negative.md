# Negative case: scan-toml-security

Expected result: do not invoke `scan-toml-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-toml-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-toml-security`.

Skill description for comparison:

```text
Scans TOML configuration files including pyproject, Cargo, service, and application configs for plaintext credentials, disabled TLS, debug mode, wildcard exposure, and unsafe dependency source settings.
```
