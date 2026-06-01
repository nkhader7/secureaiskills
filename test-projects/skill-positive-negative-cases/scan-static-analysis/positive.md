# Positive case: scan-static-analysis

Expected result: invoke `scan-static-analysis`.

User request:

```text
/scan-static-analysis D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-static-analysis workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-static-analysis\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Runs or plans static analysis using CodeQL, Semgrep, and SARIF processing. Use when scanning a workspace for vulnerabilities, selecting CodeQL or Semgrep rulesets, generating a SAST scan plan, processing SARIF results, or combining static-analysis findings from multiple tools.
- Uses the explicit trigger `/scan-static-analysis`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js
- src/client.js

Expected evidence signals:
- eval(req.body.expression)
- exec('convert ' + req.query.file
- innerHTML

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-static-analysis\report.md

