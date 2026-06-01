---
name: scan-xml-security
description: Scans XML files including application configs, manifests, SAML metadata, SOAP definitions, and parser settings for XXE, insecure parser flags, plaintext credentials, weak transport, and disabled security constraints.
triggers:
  - /scan-xml-security
  - "scan.*xml.*security"
  - "review.*xml.*config"
  - "check.*xxe"
  - "audit.*saml.*xml"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
  owasp_cheatsheets: ../_shared/owasp-cheatsheets.yaml
---

# scan-xml-security

Scan XML documents and configuration files for XML-specific and configuration security risks.

## Orchestration

1. Load `references/rules.yaml` to get the active `XML-` rule set.
2. Include `*.xml`, `*.xsd`, `*.wsdl`, and XML-like config files from user-supplied paths or changed files.
3. Preserve element and attribute context when possible, such as `web-app/security-constraint`.
4. Evaluate each rule using its `match_strategy`, capturing file, line, snippet, and confidence.
5. Mark each rule `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable`.
6. Render the final report using `references/report-template.md`.

## Usage

Scan XML files in the current change:

```text
/scan-xml-security
```

Scan a specific XML config:

```text
/scan-xml-security config/web.xml metadata/
```

## Review Guidance

Prioritize parser behavior, external entities, inline credentials, disabled transport security, and authentication constraints.
