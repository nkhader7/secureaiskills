# Positive case: scan-for-ssrf

Expected result: invoke `scan-for-ssrf`.

User request:

```text
/scan-for-ssrf D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-for-ssrf workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-ssrf\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Detects Server-Side Request Forgery (SSRF) vulnerabilities including user-controlled HTTP sinks, cloud metadata endpoint access, internal network probing, and unsafe redirect patterns. Use when reviewing code that makes outbound HTTP requests, fetches remote URLs, or accepts hostnames from user input.
- Uses the explicit trigger `/scan-for-ssrf`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js

Expected evidence signals:
- axios.get(req.query.url
- 169.254.169.254
- maxRedirects

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-ssrf\report.md

