# Negative case: scan-iac-security

Expected result: do not invoke `scan-iac-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-iac-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-iac-security`.

Skill description for comparison:

```text
Scans infrastructure-as-code changes for security misconfigurations in Terraform, CloudFormation, ARM/Bicep, Pulumi config, and related IaC files.
```
