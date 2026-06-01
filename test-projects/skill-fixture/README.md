# Skill Fixture Project

This is a deliberately vulnerable local fixture used to exercise the security
skills in this repository. It is not an application template and should never be
deployed.

The fixture contains controlled evidence for:

- Broken access control, IDOR, tenant isolation, and unsafe CORS.
- Authentication and session management mistakes.
- Weak cryptography and unsafe token generation.
- Injection, XSS, SSRF, and unsafe exception handling.
- Missing security headers and weak logging behavior.
- Vulnerable third-party packages, SBOM data, and dependency graph evidence.
- Docker, Kubernetes, IaC, API, CI/CD, and software supply-chain risks.
- YAML, JSON, Markdown, XML, and TOML configuration/documentation risks.
- Threat-model and ASVS review evidence.

Run the local coverage check from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File test-projects/skill-fixture/run-fixture-check.ps1
```

Run the full combination suite and regenerate the report graphs:

```powershell
powershell -ExecutionPolicy Bypass -File test-projects/skill-fixture/run-all-skill-combinations.ps1
```

The checker only verifies that each skill has target evidence in the fixture.
The actual skills still need to reason over the evidence and produce findings.
