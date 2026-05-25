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
- `audit-asvs-compliance`
- `scan-api-security`
- `detect-supply-chain-risks`
- `generate-dependency-graph`

### Development Phase

Use these skills while code, infrastructure, and dependencies are being added:

- `detect-secrets`
- `scan-for-injection`
- `scan-static-analysis`
- `audit-crypto-usage`
- `run-sast`
- `scan-sca-dependencies`
- `generate-sbom`
- `scan-iac-security`
- `scan-k8s-manifests`
- `scan-container-image`

## Current Skills

| Skill | Trigger | Rule Prefix | Rules | Status |
|-------|---------|-------------|-------|--------|
| [detect-secrets](skills/detect-secrets/SKILL.md) | `/detect-secrets` | `DS-`, `GITLEAKS-`, `TITUS-RULE-` | 393 | Ready |
| [scan-for-injection](skills/scan-for-injection/SKILL.md) | `/scan-for-injection` | `SI-` | 7 | Ready |
| [scan-iac-security](skills/scan-iac-security/SKILL.md) | `/scan-iac-security` | `IAC-` | 1746 | Ready |
| [scan-api-security](skills/scan-api-security/SKILL.md) | `/scan-api-security` | `SA-` | 6 | Ready |
| [scan-static-analysis](skills/scan-static-analysis/SKILL.md) | `/scan-static-analysis` | `SAS-` | 30 | Ready |
| [scan-container-image](skills/scan-container-image/SKILL.md) | `/scan-container-image` | `CIS-DOCKER-` | 118 | Ready |
| [scan-kubernetes-manifests](skills/scan-kubernetes-manifests/SKILL.md) | `/scan-kubernetes-manifests` | `CIS-K8S-` | 131 | Ready |
| [audit-asvs-compliance](skills/audit-asvs-compliance/SKILL.md) | `/audit-asvs-compliance` | `ASVS-` | 345 | Ready |
| [threat-model-system](skills/threat-model-system/SKILL.md) | `/threat-model-system` | `TMS-` | 12 | Ready |
| audit-crypto-usage | `/audit-crypto-usage` | `ACU-` | — | Planned |
| scan-sca-dependencies | `/scan-sca-dependencies` | `SCA-` | — | Planned |
| detect-supply-chain-risks | `/detect-supply-chain-risks` | `SCR-` | — | Planned |
| generate-sbom | `/generate-sbom` | — | — | Planned |

## Validation Status

All skills are validated against a common checklist before being marked Ready. Each skill must pass:

| Check | Description |
|-------|-------------|
| Required files | `SKILL.md`, `references/rules.yaml`, `references/report-template.md` all present |
| Frontmatter | `name`, `description`, `triggers`, `references` all declared |
| References wired | `rules`, `report_template`, `base_report` all resolve to real paths |
| Trigger alignment | First slash trigger matches the skill `name` field |
| Sections present | `## Orchestration` and `## Usage` both in body |
| Rules defined | At least one rule in `rules.yaml` with a valid `version:` |
| No empty patterns | No rule has `patterns: []` |
| Valid severity | Every rule uses `Critical`, `High`, `Medium`, `Low`, or `Info` |
| Remediation present | Every rule includes a `remediation:` field |
| Template contract | `{{target}}`, `{{date}}`, `{{#each findings}}`, `{{#if no_findings}}` all present |

**Current result: 9 / 9 skills pass all checks — 2,681 rules across all skills.**

## Suggested Skills for Application Security

The following skills cover gaps in the current set, mapped to OWASP and industry-standard security domains.

### High priority — gaps in OWASP Top 10 2021 coverage

| Skill | Trigger | Covers | Rule Prefix |
|-------|---------|--------|-------------|
| `audit-crypto-usage` | `/audit-crypto-usage` | Weak algorithms (MD5/SHA1/RC4/DES), insecure PRNG, missing key rotation, TLS misconfiguration — **A02:2021** | `ACU-` |
| `scan-broken-access-control` | `/scan-broken-access-control` | Missing auth checks, IDOR patterns, path traversal, privilege escalation, CORS — **A01:2021** | `BAC-` |
| `scan-for-xss` | `/scan-for-xss` | Reflected, stored, and DOM-based XSS; unsafe innerHTML; missing CSP — **A03:2021** | `XSS-` |
| `audit-logging-monitoring` | `/audit-logging-monitoring` | Missing security event logging, sensitive data in logs, log injection, audit-trail gaps — **A09:2021** | `ALM-` |

### Medium priority — supply chain and dependency risk

| Skill | Trigger | Covers | Rule Prefix |
|-------|---------|--------|-------------|
| `scan-sca-dependencies` | `/scan-sca-dependencies` | Known CVEs in `package.json`, `requirements.txt`, `pom.xml`, `go.mod`; outdated or unmaintained packages — **A06:2021** | `SCA-` |
| `detect-supply-chain-risks` | `/detect-supply-chain-risks` | Dependency confusion, typosquatting, unpinned Actions, malicious package indicators, CI/CD injection | `SCR-` |
| `generate-sbom` | `/generate-sbom` | SPDX/CycloneDX software bill of materials, dependency inventory, license mapping | — |

### Medium priority — runtime and data exposure

| Skill | Trigger | Covers | Rule Prefix |
|-------|---------|--------|-------------|
| `scan-security-headers` | `/scan-security-headers` | Missing HSTS, CSP, X-Frame-Options, X-Content-Type-Options; permissive CORS; insecure cookie flags — **A05:2021** | `SHD-` |
| `scan-for-ssrf` | `/scan-for-ssrf` | SSRF sinks, cloud metadata endpoint access, blind SSRF patterns — **A10:2021** | `SSRF-` |
| `scan-for-pii` | `/scan-for-pii` | PII patterns in code and logs (email, SSN, card numbers, health data), unmasked sensitive fields | `PII-` |

### Lower priority — advanced and specialised

| Skill | Trigger | Covers | Rule Prefix |
|-------|---------|--------|-------------|
| `scan-ci-cd-security` | `/scan-ci-cd-security` | GitHub Actions injection, unpinned dependencies, leaked secrets in pipelines, self-hosted runner risk | `CICD-` |
| `audit-session-management` | `/audit-session-management` | Session fixation, insecure storage, missing timeout, cookie security, JWT expiry | `SM-` |
| `generate-dependency-graph` | `/generate-dependency-graph` | Transitive dependency map, trust-boundary visualisation for third-party code | — |

### Coverage map against OWASP Top 10 2021

| OWASP Category | Current coverage | Planned skill |
|----------------|-----------------|---------------|
| A01 Broken Access Control | scan-for-injection (partial) | `scan-broken-access-control` |
| A02 Cryptographic Failures | — | `audit-crypto-usage` |
| A03 Injection | **scan-for-injection** ✓ | `scan-for-xss` (XSS sub-type) |
| A04 Insecure Design | **threat-model-system** ✓ | — |
| A05 Security Misconfiguration | **scan-iac-security**, **scan-container-image**, **scan-kubernetes-manifests** ✓ | `scan-security-headers` |
| A06 Vulnerable Components | — | `scan-sca-dependencies` |
| A07 Auth & Session Failures | audit-asvs-compliance (partial) | `audit-session-management` |
| A08 Software Integrity Failures | — | `detect-supply-chain-risks` |
| A09 Logging & Monitoring | — | `audit-logging-monitoring` |
| A10 SSRF | — | `scan-for-ssrf` |

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

## Architecture — How the LLM Works on Skill Invocation

```
╔══════════════════════════════════════════════════════════════════════════════╗
║               SKILL INVOCATION — HIGH-LEVEL ARCHITECTURE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  USER                                                                    │
  │  /detect-secrets  ·  /scan-iac-security  ·  "scan this for secrets"     │
  └─────────────────────────────────┬────────────────────────────────────────┘
                                    │ slash command or natural-language trigger
                                    ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  CONTEXT ASSEMBLY                                                        │
  │                                                                          │
  │  ┌───────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
  │  │    SKILL.md       │  │     rules.yaml        │  │ report-template  │  │
  │  │───────────────────│  │──────────────────────│  │──────────────────│  │
  │  │ name / triggers   │  │ id · severity         │  │ {{findings}}     │  │
  │  │ references map    │  │ patterns              │  │ {{#each}} loops  │  │
  │  │ orchestration     │  │ match_strategy        │  │ {{snippet}}      │  │
  │  │ steps 1–N         │  │ remediation           │  │ summary table    │  │
  │  └────────┬──────────┘  └──────────┬────────────┘  └────────┬─────────┘  │
  │           │                        │                         │            │
  │           └────────────────────────┴─────────────────────────┘            │
  │                                    │                                      │
  │                                    ▼                                      │
  │               ┌────────────────────────────────────────┐                 │
  │               │          LLM CONTEXT WINDOW            │                 │
  │               │  instructions + rules + output schema  │                 │
  │               │         all loaded simultaneously      │                 │
  │               └────────────────────────────────────────┘                 │
  └──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ orchestration: identify target files
                                    ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  TARGET IDENTIFICATION                                                   │
  │  git diff main...HEAD  ·  user-supplied path  ·  --all flag             │
  │  skip: binaries · lock files · .gitignore · node_modules · .terraform/  │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                 │ file content added to context
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  LLM EVALUATION  (per file × per rule)                                  │
  │                                                                          │
  │  match_strategy                                                          │
  │  ┌──────────────────┬─────────────────────────────────────────────────┐ │
  │  │ regex            │ scan lines for pattern matches                  │ │
  │  │ resource_context │ flag only when pattern group co-occurs in block │ │
  │  │ design_review    │ evaluate rule as evidence question              │ │
  │  └──────────────────┴─────────────────────────────────────────────────┘ │
  │                                                                          │
  │  match found → finding { file · line · rule_id · severity · snippet }   │
  │                                                                          │
  │  aggregate by severity:  Critical → High → Medium → Low → Info          │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  REPORT GENERATION                                                       │
  │                                                                          │
  │  findings[]  +  report-template.md                                       │
  │       │                                                                  │
  │       └─► fill {{placeholders}}  ·  expand {{#each findings}} loops     │
  │           mask secrets → ***REDACTED***  ·  compute severity counts      │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  MARKDOWN REPORT  (streamed to user)                                     │
  │  Summary table · Findings with file/line/snippet/remediation · Actions   │
  └──────────────────────────────────────────────────────────────────────────┘
```

**Three files drive everything:**

| File | Role | What the LLM does with it |
|------|------|--------------------------|
| `SKILL.md` | Instructions | Reads frontmatter to resolve file paths, follows orchestration steps as its working plan |
| `rules.yaml` | Knowledge | Loads all rules into context; uses `patterns` as matching criteria and `remediation` as verbatim output |
| `report-template.md` | Output contract | Fills every `{{placeholder}}`, expands loops, and suppresses empty sections |

**Pattern evaluation** — the LLM does not compile or execute regex patterns as code. It reads each pattern as a semantic instruction and applies code-reading reasoning to find matches. `match_strategy` controls how: `regex` finds literal pattern matches line by line; `resource_context` requires a group of patterns to co-occur in the same resource block before flagging; `design_review` treats the rule as an evidence question evaluated against design artifacts.

**Context budget** — rules files range from 7 rules (`scan-for-injection`) to 1746 rules (`scan-iac-security`). All rules are loaded into the context window simultaneously alongside the file being scanned. For large rule sets, high-severity rules are prioritised if the window approaches its limit.

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
