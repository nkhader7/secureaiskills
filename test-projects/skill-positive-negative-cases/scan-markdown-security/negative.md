# Negative case: scan-markdown-security

Expected result: do not invoke `scan-markdown-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-markdown-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-markdown-security`.

Skill description for comparison:

```text
Scans Markdown documentation, runbooks, READMEs, and design notes for security risks including leaked credentials, unsafe operational commands, disabled security controls, insecure examples, and missing threat-model evidence.
```
