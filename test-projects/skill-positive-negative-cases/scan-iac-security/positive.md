# Positive case: scan-iac-security

Expected result: invoke `scan-iac-security`.

User request:

```text
/scan-iac-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-iac-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-iac-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans infrastructure-as-code changes for security misconfigurations in Terraform, CloudFormation, ARM/Bicep, Pulumi config, and related IaC files.
- Uses the explicit trigger `/scan-iac-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- infra/main.tf

Expected evidence signals:
- 0.0.0.0/0
- acl    = "public-read"
- encrypted         = false

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-iac-security\report.md

