# Negative case: scan-security-headers

Expected result: do not invoke `scan-security-headers`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-security-headers`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-security-headers`.

Skill description for comparison:

```text
Scans web applications, APIs, reverse proxies, CDN configuration, and middleware for missing or unsafe HTTP security headers, cookie flags, CORS policy, CSP, HSTS, clickjacking protections, MIME sniffing protections, referrer policy, and browser-facing misconfiguration.
```
