# Negative case: scan-xml-security

Expected result: do not invoke `scan-xml-security`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-xml-security`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-xml-security`.

Skill description for comparison:

```text
Scans XML files including application configs, manifests, SAML metadata, SOAP definitions, and parser settings for XXE, insecure parser flags, plaintext credentials, weak transport, and disabled security constraints.
```
