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
+-- scan-for-xss/
+-- scan-for-ssrf/
+-- scan-broken-access-control/
+-- audit-auth-session-management/
+-- audit-crypto-usage/
+-- audit-logging-monitoring/
+-- scan-exception-handling/
+-- scan-sca-dependencies/
+-- detect-supply-chain-risks/
+-- generate-sbom/
+-- generate-dependency-graph/
+-- scan-iac-security/
+-- scan-kubernetes-manifests/
+-- scan-container-image/
+-- scan-security-headers/
+-- scan-api-security/
+-- scan-static-analysis/
`-- audit-asvs-compliance/
```

These names are readable, automation-friendly, and grouped around what the skill does. Detection skills find concrete evidence, audit skills review a security domain, and generation skills produce security artifacts that other skills can consume.

## Skill Lifecycle Focus

### Design Phase

Use these skills before implementation begins or when a design changes:

- `threat-model-system`
- `audit-asvs-compliance`
- `scan-api-security`
- `scan-broken-access-control`
- `audit-auth-session-management`
- `audit-crypto-usage`
- `detect-supply-chain-risks`
- `generate-dependency-graph`

### Development Phase

Use these skills while code, infrastructure, containers, and dependencies are being added:

- `detect-secrets`
- `scan-for-injection`
- `scan-for-xss`
- `scan-for-ssrf`
- `scan-static-analysis`
- `scan-sca-dependencies`
- `generate-sbom`
- `scan-iac-security`
- `scan-kubernetes-manifests`
- `scan-container-image`
- `scan-security-headers`
- `scan-exception-handling`
- `audit-logging-monitoring`

## Current Skills

| Skill | Trigger | Rule Prefix | Rules | Status |
|-------|---------|-------------|-------|--------|
| [detect-secrets](skills/detect-secrets/SKILL.md) | `/detect-secrets` | `DS-, GITLEAKS-, TITUS-RULE-` | 393 | Ready |
| [scan-for-injection](skills/scan-for-injection/SKILL.md) | `/scan-for-injection` | `SI-` | 7 | Ready |
| [scan-iac-security](skills/scan-iac-security/SKILL.md) | `/scan-iac-security` | `IAC-` | 1746 | Ready |
| [scan-api-security](skills/scan-api-security/SKILL.md) | `/scan-api-security` | `SA-` | 6 | Ready |
| [scan-static-analysis](skills/scan-static-analysis/SKILL.md) | `/scan-static-analysis` | `SAS-` | 30 | Ready |
| [scan-container-image](skills/scan-container-image/SKILL.md) | `/scan-container-image` | `CIS-DOCKER-`, `DTOP-` | 128 | Ready |
| [scan-kubernetes-manifests](skills/scan-kubernetes-manifests/SKILL.md) | `/scan-kubernetes-manifests` | `CIS-K8S-` | 131 | Ready |
| [audit-asvs-compliance](skills/audit-asvs-compliance/SKILL.md) | `/audit-asvs-compliance` | `ASVS-` | 345 | Ready |
| [threat-model-system](skills/threat-model-system/SKILL.md) | `/threat-model-system` | `TMS-` | 12 | Ready |
| [scan-broken-access-control](skills/scan-broken-access-control/SKILL.md) | `/scan-broken-access-control` | `BAC-` | 12 | Ready |
| [audit-auth-session-management](skills/audit-auth-session-management/SKILL.md) | `/audit-auth-session-management` | `ASM-` | 12 | Ready |
| [audit-crypto-usage](skills/audit-crypto-usage/SKILL.md) | `/audit-crypto-usage` | `ACU-` | 12 | Ready |
| [audit-logging-monitoring](skills/audit-logging-monitoring/SKILL.md) | `/audit-logging-monitoring` | `ALM-` | 12 | Ready |
| [scan-exception-handling](skills/scan-exception-handling/SKILL.md) | `/scan-exception-handling` | `EXC-` | 10 | Ready |
| [scan-security-headers](skills/scan-security-headers/SKILL.md) | `/scan-security-headers` | `SHD-` | 12 | Ready |
| [scan-for-xss](skills/scan-for-xss/SKILL.md) | `/scan-for-xss` | `XSS-` | 12 | Ready |
| [scan-for-ssrf](skills/scan-for-ssrf/SKILL.md) | `/scan-for-ssrf` | `SSRF-` | 8 | Ready |
| [scan-sca-dependencies](skills/scan-sca-dependencies/SKILL.md) | `/scan-sca-dependencies` | `SCA-`, `OSS-RISK-` | 28 | Ready |
| [detect-supply-chain-risks](skills/detect-supply-chain-risks/SKILL.md) | `/detect-supply-chain-risks` | `SCR-` | 20 | Ready |
| [generate-sbom](skills/generate-sbom/SKILL.md) | `/generate-sbom` | `SBOM-` | 10 | Ready |
| [generate-dependency-graph](skills/generate-dependency-graph/SKILL.md) | `/generate-dependency-graph` | `DG-` | 10 | Ready |

## Validation Status

All skills are validated against a common checklist before being marked Ready. Each skill must pass:

| Check | Description |
|-------|-------------|
| Required files | `SKILL.md`, `references/rules.yaml`, `references/report-template.md` all present |
| Frontmatter | `name`, `description`, `triggers`, `references` all declared |
| References wired | `rules`, `report_template`, `base_report`, and optional shared guidance files all resolve to real paths |
| Trigger alignment | First slash trigger matches the skill `name` field |
| Sections present | `## Orchestration` and `## Usage` both in body |
| Rules defined | At least one rule in `rules.yaml` with a valid `version:` |
| No empty patterns | No rule has `patterns: []` |
| Valid severity | Every rule uses `Critical`, `High`, `Medium`, `Low`, or `Info` |
| Match strategy | Every rule declares `match_strategy`, or the rule file declares a safe `default_match_strategy` |
| Remediation present | Every rule includes a `remediation:` field |
| Template contract | `{{target}}`, `{{date}}`, `{{#each findings}}`, `{{#if no_findings}}` all present |

**Current result: 21 / 21 skills pass all checks — 2,956 rules across all skills.**

## Application Security Coverage

The current skill set maps to OWASP Top 10 2025 categories and supporting supply-chain artifacts. `scan-sca-dependencies` focuses on vulnerable third-party packages and reports package name, installed version, CVE, severity, fixed version, direct/transitive relationship, dependency path, and remediation owner. `detect-supply-chain-risks` is separate: it reviews trust and provenance risks such as dependency confusion, typosquatting, unsigned artifacts, unpinned CI actions, mutable container tags, weak build isolation, and missing attestation. `generate-dependency-graph` supports both by explaining direct and transitive dependency paths.

| OWASP Top 10 2025 Category | Covered By |
|----------------------------|------------|
| A01 Broken Access Control | `scan-broken-access-control`, `scan-api-security`, `audit-asvs-compliance` |
| A02 Security Misconfiguration | `scan-iac-security`, `scan-container-image`, `scan-kubernetes-manifests`, `scan-security-headers` |
| A03 Software Supply Chain Failures | `scan-sca-dependencies`, `detect-supply-chain-risks`, `generate-sbom`, `generate-dependency-graph` |
| A04 Cryptographic Failures | `audit-crypto-usage`, `audit-asvs-compliance` |
| A05 Injection | `scan-for-injection`, `scan-for-xss`, `scan-for-ssrf` |
| A06 Insecure Design | `threat-model-system`, `audit-asvs-compliance` |
| A07 Authentication Failures | `audit-auth-session-management`, `scan-api-security`, `audit-asvs-compliance` |
| A08 Software or Data Integrity Failures | `detect-supply-chain-risks`, `generate-sbom`, `scan-sca-dependencies` |
| A09 Security Logging and Alerting Failures | `audit-logging-monitoring`, `scan-container-image`, `scan-kubernetes-manifests` |
| A10 Mishandling of Exceptional Conditions | `scan-exception-handling`, `scan-api-security` |

### External Guidance Fit

OWASP Cheat Sheet Series content is wired through [skills/_shared/owasp-cheatsheets.yaml](skills/_shared/owasp-cheatsheets.yaml). Each skill loads that shared map and uses the relevant cheat sheets as authoritative remediation and review references. For example, the Access Control, Authorization, Authorization Testing Automation, IDOR, and Mass Assignment sheets support `scan-broken-access-control`; the Authentication, Session Management, MFA, Password Storage, JWT, OAuth2, and SAML sheets support `audit-auth-session-management`; Software Supply Chain, Dependency Graph/SBOM, CI/CD, GitHub Actions, and NPM sheets support the SCA and supply-chain skills.

## Repository Structure

```text
skills/
+-- _shared/
|   +-- base-report.md
|   `-- owasp-cheatsheets.yaml
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

**Core files drive each skill:**

| File | Role | What the LLM does with it |
|------|------|--------------------------|
| `SKILL.md` | Instructions | Reads frontmatter to resolve file paths, follows orchestration steps as its working plan |
| `rules.yaml` | Knowledge | Loads all rules into context; uses `patterns` as matching criteria and `remediation` as verbatim output |
| `report-template.md` | Output contract | Fills every `{{placeholder}}`, expands loops, and suppresses empty sections |
| `_shared/owasp-cheatsheets.yaml` | Guidance map | Maps each skill to relevant OWASP Cheat Sheet Series references for remediation and review support |

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
