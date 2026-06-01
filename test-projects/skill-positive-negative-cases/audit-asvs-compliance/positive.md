# Positive case: audit-asvs-compliance

Expected result: invoke `audit-asvs-compliance`.

User request:

```text
/audit-asvs-compliance D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the audit-asvs-compliance workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-asvs-compliance\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Audits an application, API, design, or codebase against OWASP Application Security Verification Standard 5.0 requirements. Use when reviewing ASVS compliance, mapping implementation evidence to ASVS controls, producing an ASVS gap assessment, or checking application security requirements by ASVS level.
- Uses the explicit trigger `/audit-asvs-compliance`.
- Points at known fixture evidence for this skill.

Fixture targets:
- docs/design.md
- src/app.js
- api/openapi.yaml

Expected evidence signals:
- ASVS
- Missing authorization
- Session cookie

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\audit-asvs-compliance\report.md

