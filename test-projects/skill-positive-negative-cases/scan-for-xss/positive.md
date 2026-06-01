# Positive case: scan-for-xss

Expected result: invoke `scan-for-xss`.

User request:

```text
/scan-for-xss D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-for-xss workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-xss\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans frontend and backend code for cross-site scripting risks including reflected XSS, stored XSS, DOM XSS, unsafe HTML sinks, unsafe template rendering, missing output encoding, sanitizer misuse, unsafe markdown rendering, and weak Content Security Policy.
- Uses the explicit trigger `/scan-for-xss`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/client.js
- src/app.js

Expected evidence signals:
- innerHTML
- dangerouslySetInnerHTML
- res.send('<h1>' + req.query.name

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-for-xss\report.md

