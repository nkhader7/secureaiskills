# Negative case: audit-crypto-usage

Expected result: do not invoke `audit-crypto-usage`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/audit-crypto-usage`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `audit-crypto-usage`.

Skill description for comparison:

```text
Audits code and configuration for cryptographic failures including weak algorithms, insecure random number generation, poor key management, unsafe TLS, missing encryption, weak password hashing, hardcoded keys, and misuse of crypto APIs.
```
