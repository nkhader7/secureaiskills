# Negative case: audit-asvs-compliance

Expected result: do not invoke `audit-asvs-compliance`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/audit-asvs-compliance`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `audit-asvs-compliance`.

Skill description for comparison:

```text
Audits an application, API, design, or codebase against OWASP Application Security Verification Standard 5.0 requirements. Use when reviewing ASVS compliance, mapping implementation evidence to ASVS controls, producing an ASVS gap assessment, or checking application security requirements by ASVS level.
```
