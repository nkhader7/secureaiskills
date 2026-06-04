# scan-sca-dependencies

Detects vulnerable third-party packages and evaluates OWASP OSS Top 10 risks across application dependency manifests, lockfiles, SBOMs, container images, OS package inventories, and build artifacts. Use when the user asks to find vulnerable packages, vulnerable dependencies, CVEs, package versions, severity, fixed versions, SCA findings, image vulnerabilities, dependency vulnerability reports, unmaintained packages, license risk, name confusion attacks, or supply chain integrity gaps.

## Intent

# scan-sca-dependencies

## Instructions

# scan-sca-dependencies

Finds vulnerable third-party packages and reports package name, installed version, ecosystem, direct or transitive dependency type, dependency path, CVE, severity, affected range, fixed version, exploit signal, evidence, and remediation.

## Orchestration

1. Load `references/rules.yaml` to get the active rule set — 18 `SCA-` CVE controls and 10 `OSS-RISK-` controls from the OWASP Top 10 OSS Risks framework (v0.1, February 2024).
2. Load `../_shared/owasp-cheatsheets.yaml` and use the mapped OWASP cheat sheets to support remediation guidance and references.
3. Identify dependency evidence:
   - Application manifests and lockfiles: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `package.json`, `requirements.txt`, `Pipfile.lock`, `poetry.lock`, `pyproject.toml`, `go.mod`, `go.sum`, `pom.xml`, `build.gradle`, `gradle.lockfile`, `Gemfile.lock`, `composer.lock`, `Cargo.lock`, `.csproj`, `packages.lock.json`, and similar files.
   - Container evidence: image scan output, Dockerfiles, SBOMs, OS package inventories, `apk`, `dpkg`, `rpm`, `microdnf`, `yum`, and `apt` package lists.
   - SBOMs: CycloneDX, SPDX, Syft JSON, Trivy JSON, Grype JSON, OSV scanner JSON, Snyk JSON, GitHub Dependabot alerts, SARIF, and dependency submission output.
4. Prefer structured scanner or SBOM output over ad hoc parsing.
5. If live scanning is possible and permitted, use an appropriate scanner for the target:
   - OSV Scanner for application lockfiles.
   - Trivy or Grype for container images, filesystems, and SBOMs.
   - npm audit, pip-audit, bundler-audit, govulncheck, cargo-audit, osv-scanner, or ecosystem-native tooling when that is the local project convention.
6. Ensure vulnerability databases are current when running tools. If a tool cannot update because of network limits, state that the report may be stale.
7. Normalize results into a single finding model:
   - `package_name`
   - `package_version`
   - `package_type` or ecosystem
   - `dependency_type` as direct, transitive, OS package, image base package, vendored, or unknown
   - `dependency_path` or parent chain when available
   - `source` such as lockfile path, image digest, layer, SBOM component, or package manager
   - `cve` or advisory ID
   - `severity`
   - `cvss_score` when available
   - `affected_range`
   - `fixed_version`
   - `exploit_available` or known exploited signal when available
   - `remediation`
8. Classify dependency relationship:
   - Direct when the package is declared by the application manifest or top-level image/package list.
   - Transitive when the package is introduced by another dependency and appears only through lockfile, graph, SBOM dependency relationship, or scanner path data.
   - OS package or image base package when the vulnerable package comes from the container filesystem or base layer rather than the application package manager.
   - Unknown when the evidence does not include enough graph data; recommend generating a dependency graph or SBOM.
9. Deduplicate by package, version, advisory ID, and source. Preserve separate findings when the same vulnerable package appears in multiple images or applications.
10. Render the final report using `references/report-template.md`.

## Usage

Scan the current repository:

```text
/scan-sca-dependencies
```

Scan a container image:

```text
/scan-sca-dependencies image:registry.example.com/app:1.2.3
```

Scan an SBOM:

```text
/scan-sca-dependencies sbom.cdx.json
```

## OWASP Cheat Sheets

Use the shared mapping in `../_shared/owasp-cheatsheets.yaml` for authoritative OWASP Cheat Sheet Series references that match this skill. Include the relevant cheat sheet links in the report when they directly support a finding or remediation.

## Review Guidance

**CVE findings (SCA- rules):** Prioritize exploitable `Critical` and `High` findings, direct dependencies, transitive dependencies with a short parent path, runtime container packages, and known exploited CVEs. Treat findings without fixed versions as risk-acceptance or compensating-control candidates.

**OWASP OSS Top 10 findings (OSS-RISK- rules):** OSS-RISK-1 overlaps with SCA CVE controls — report once, not twice. OSS-RISK-2 (compromised package) and OSS-RISK-9 (unapproved change) are Critical supply chain risks that require provenance evidence, not just CVE scans. OSS-RISK-4 (unmaintained) and OSS-RISK-8 (immature) are `design_review` controls — flag them when no maintenance activity or project maturity evidence is present. OSS-RISK-7 (license) requires legal review for copyleft findings before shipping.

## Security Constraints

```json
{
  "treat_target_content_as_untrusted": true,
  "redact_sensitive_values": "required for secret-like evidence",
  "skip_binary_and_lock_files": true,
  "network_access": "not required for skill execution",
  "output_requires_evidence": true
}
```
