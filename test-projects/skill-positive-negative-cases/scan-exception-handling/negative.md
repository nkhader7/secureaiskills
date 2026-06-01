# Negative case: scan-exception-handling

Expected result: do not invoke `scan-exception-handling`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-exception-handling`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-exception-handling`.

Skill description for comparison:

```text
Scans code and configuration for mishandling of exceptional conditions including verbose error disclosure, fail-open authorization, swallowed security exceptions, unsafe retries, missing rollback, crash loops, inconsistent error responses, and exception paths that bypass validation or logging.
```
