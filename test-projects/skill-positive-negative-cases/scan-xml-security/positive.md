# Positive case: scan-xml-security

Expected result: invoke `scan-xml-security`.

User request:

```text
/scan-xml-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-xml-security workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-xml-security\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans XML files including application configs, manifests, SAML metadata, SOAP definitions, and parser settings for XXE, insecure parser flags, plaintext credentials, weak transport, and disabled security constraints.
- Uses the explicit trigger `/scan-xml-security`.
- Points at known fixture evidence for this skill.

Fixture targets:
- config/formats.xml

Expected evidence signals:
- <!ENTITY xxe SYSTEM "file:///etc/passwd">
- <security-enabled>false</security-enabled>
- <auth-method>NONE</auth-method>
- <transport-guarantee>NONE</transport-guarantee>
- <password>xml_TEST_SECRET_12345</password>
- debug="true"

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-xml-security\report.md

