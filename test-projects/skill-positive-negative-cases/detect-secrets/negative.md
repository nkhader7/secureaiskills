# Negative case: detect-secrets

Expected result: do not invoke `detect-secrets`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/detect-secrets`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `detect-secrets`.

Skill description for comparison:

```text
Detects hardcoded secrets, credentials, and sensitive tokens committed to source code
```
