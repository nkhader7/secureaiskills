# Positive case: scan-security-headers

Expected result: invoke `scan-security-headers`.

User request:

```text
/scan-security-headers D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-security-headers workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-security-headers\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans web applications, APIs, reverse proxies, CDN configuration, and middleware for missing or unsafe HTTP security headers, cookie flags, CORS policy, CSP, HSTS, clickjacking protections, MIME sniffing protections, referrer policy, and browser-facing misconfiguration.
- Uses the explicit trigger `/scan-security-headers`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js
- nginx.conf

Expected evidence signals:
- X-Powered-By
- Access-Control-Allow-Origin "*"
- helmet({ contentSecurityPolicy: false

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-security-headers\report.md

