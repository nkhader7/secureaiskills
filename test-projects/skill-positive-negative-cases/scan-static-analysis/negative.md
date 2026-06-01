# Negative case: scan-static-analysis

Expected result: do not invoke `scan-static-analysis`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-static-analysis`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-static-analysis`.

Skill description for comparison:

```text
Runs or plans static analysis using CodeQL, Semgrep, and SARIF processing. Use when scanning a workspace for vulnerabilities, selecting CodeQL or Semgrep rulesets, generating a SAST scan plan, processing SARIF results, or combining static-analysis findings from multiple tools.
```
