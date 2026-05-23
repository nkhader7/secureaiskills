# secureaiskills

Security-focused skills for development teams building products, services, and applications.

The main intent of this repository is to provide reusable skills that can be invoked during the design and development phases to detect security risks early. The first set of skills should focus on detection, review, and evidence generation. Later, the repository can expand into remediation guidance, policy enforcement, secure design patterns, and workflow automation.

## Naming Convention

Use short, kebab-case names that start with a clear action verb.

Preferred verbs:

- `detect-*` for finding a specific risk or risky pattern.
- `scan-*` for inspecting a target such as code, dependencies, APIs, IaC, Kubernetes, or containers.
- `audit-*` for deeper review of a specific security domain.
- `generate-*` for producing security artifacts such as SBOMs or dependency graphs.
- `run-*` only when the skill orchestrates an external tool or toolchain.

Keep names:

- lowercase
- kebab-case
- action-oriented
- specific to the security outcome
- stable enough to grow into automation later

Avoid names that are too broad, such as `security-review`, unless the skill is intentionally a general umbrella workflow.

## Suggested Skill Set

```text
skills/
+-- threat-model-system/
+-- detect-secrets/
+-- scan-for-injection/
+-- audit-crypto-usage/
+-- run-sast/
+-- scan-sca-dependencies/
+-- generate-sbom/
+-- generate-dependency-graph/
+-- detect-supply-chain-risks/
+-- scan-iac-security/
+-- scan-k8s-manifests/
+-- scan-container-image/
`-- scan-api-security/
```

These names are a good starting point. They are readable, automation-friendly, and grouped around what the skill does.

One possible refinement is to keep the object names consistent:

```text
detect-secrets
detect-injection-risks
audit-crypto-usage
run-sast
scan-dependencies
generate-sbom
generate-dependency-graph
detect-supply-chain-risks
scan-iac
scan-kubernetes-manifests
scan-container-image
scan-api-security
threat-model-system
```

## Skill Lifecycle Focus

### Design Phase

Use these skills before implementation begins or when a design changes:

- `threat-model-system`
- `scan-api-security`
- `detect-supply-chain-risks`
- `generate-dependency-graph`

### Development Phase

Use these skills while code, infrastructure, and dependencies are being added:

- `detect-secrets`
- `scan-for-injection`
- `audit-crypto-usage`
- `run-sast`
- `scan-sca-dependencies`
- `generate-sbom`
- `scan-iac-security`
- `scan-k8s-manifests`
- `scan-container-image`

## Current Skills

| Skill | Trigger | Rule Prefix | Status |
|-------|---------|-------------|--------|
| [detect-secrets](skills/detect-secrets/SKILL.md) | `/detect-secrets` | `DS-` | Ready |
| [scan-for-injection](skills/scan-for-injection/SKILL.md) | `/scan-for-injection` | `SI-` | Ready |
| threat-model-system | `/threat-model-system` | — | Planned |
| audit-crypto-usage | `/audit-crypto-usage` | — | Planned |
| run-sast | `/run-sast` | — | Planned |
| scan-sca-dependencies | `/scan-sca-dependencies` | — | Planned |
| generate-sbom | `/generate-sbom` | — | Planned |
| generate-dependency-graph | `/generate-dependency-graph` | — | Planned |
| detect-supply-chain-risks | `/detect-supply-chain-risks` | — | Planned |
| scan-iac | `/scan-iac` | — | Planned |
| scan-kubernetes-manifests | `/scan-kubernetes-manifests` | — | Planned |
| scan-container-image | `/scan-container-image` | — | Planned |
| scan-api-security | `/scan-api-security` | — | Planned |

## Repository Structure

```text
skills/
+-- _shared/
|   `-- base-report.md
`-- <skill-name>/
    +-- SKILL.md
    `-- references/
        +-- rules.yaml
        `-- report-template.md
```

## Skill Folder Convention

Each skill folder should contain:

- `SKILL.md` as the entry point and orchestration guide.
- `references/rules.yaml` for detection rules, checks, or criteria.
- `references/report-template.md` for the output format.
- Optional shared content in `skills/_shared/` when multiple skills use the same report structure or terminology.

## Current Direction

Start with detection-oriented skills that help teams answer:

- What changed?
- What risk does this introduce?
- Where is the evidence?
- How severe is it?
- What should be reviewed before merge?

This keeps the repository useful for product and application security workflows without overloading the early skills with remediation or governance concerns.
