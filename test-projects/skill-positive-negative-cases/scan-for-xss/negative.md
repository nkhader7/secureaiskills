# Negative case: scan-for-xss

Expected result: do not invoke `scan-for-xss`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-for-xss`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-for-xss`.

Skill description for comparison:

```text
Scans frontend and backend code for cross-site scripting risks including reflected XSS, stored XSS, DOM XSS, unsafe HTML sinks, unsafe template rendering, missing output encoding, sanitizer misuse, unsafe markdown rendering, and weak Content Security Policy.
```
