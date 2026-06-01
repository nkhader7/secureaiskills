# Negative case: scan-for-ssrf

Expected result: do not invoke `scan-for-ssrf`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-for-ssrf`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-for-ssrf`.

Skill description for comparison:

```text
Detects Server-Side Request Forgery (SSRF) vulnerabilities including user-controlled HTTP sinks, cloud metadata endpoint access, internal network probing, and unsafe redirect patterns. Use when reviewing code that makes outbound HTTP requests, fetches remote URLs, or accepts hostnames from user input.
```
