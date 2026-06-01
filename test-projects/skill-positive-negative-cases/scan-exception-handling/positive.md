# Positive case: scan-exception-handling

Expected result: invoke `scan-exception-handling`.

User request:

```text
/scan-exception-handling D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-exception-handling workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-exception-handling\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans code and configuration for mishandling of exceptional conditions including verbose error disclosure, fail-open authorization, swallowed security exceptions, unsafe retries, missing rollback, crash loops, inconsistent error responses, and exception paths that bypass validation or logging.
- Uses the explicit trigger `/scan-exception-handling`.
- Points at known fixture evidence for this skill.

Fixture targets:
- src/app.js

Expected evidence signals:
- res.status(500).send(err.stack)
- catch (err)
- throw err

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-exception-handling\report.md

