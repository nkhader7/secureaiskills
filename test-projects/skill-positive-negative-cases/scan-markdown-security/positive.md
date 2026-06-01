# Positive case: scan-markdown-security

Expected result: invoke `scan-markdown-security`.

User request:

```text
/scan-markdown-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-markdown-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-markdown-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans Markdown documentation, runbooks, READMEs, and design notes for security risks including leaked credentials, unsafe operational commands, disabled security controls, insecure examples, and missing threat-model evidence.
- Uses the explicit trigger `/scan-markdown-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- docs/format-security.md

Expected evidence signals:
- password: admin
- curl -k https://api.example.invalid/health
- curl https://example.invalid/install.sh | bash
- NODE_TLS_REJECT_UNAUTHORIZED=0
- AWS_ACCESS_KEY_ID_EXAMPLE
- Threat boundaries are TBD

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-markdown-security\report.md

