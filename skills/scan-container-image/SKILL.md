---
name: scan-container-image
description: Scans Dockerfiles, container image build configuration, Docker daemon/runtime configuration, Docker Compose files, Kubernetes container specs, and Docker host evidence against CIS Docker Benchmark v1.8.0 controls. Use when reviewing Docker or container security hardening, container image risks, Docker daemon settings, container runtime flags, Docker Swarm settings, or CIS Docker compliance.
triggers:
  - /scan-container-image
  - "scan.*container.*image"
  - "docker.*benchmark"
  - "cis.*docker"
  - "docker.*security"
  - "container.*runtime.*security"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# scan-container-image

Scans Docker and container-related code, configuration, and operational evidence against CIS Docker Benchmark v1.8.0.

## Orchestration

1. Load `references/rules.yaml` to get the active CIS Docker Benchmark control set.
2. Identify target evidence:
   - Default to changed Docker/container files on the current branch.
   - Include `Dockerfile*`, `docker-compose*.yml`, Compose files, Kubernetes manifests, Helm values, container build scripts, CI image-build jobs, daemon configuration, audit rules, systemd unit files, and Docker host command output when provided.
   - Scan a user-provided path when one is supplied.
3. Determine benchmark scope:
   - Use Level 1 controls for baseline Docker hardening.
   - Include Level 2 controls when the user requests stronger hardening or CIS Level 2 coverage.
   - Include Swarm controls when Docker Swarm files, commands, or architecture are in scope.
4. Evaluate each rule using `match_strategy: cis_docker_review`.
   - For `assessment_status: Automated`, look for direct configuration or command-output evidence.
   - For `assessment_status: Manual`, evaluate implementation evidence and flag missing or unclear controls as review findings.
   - Mark controls `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable`.
5. Capture recommendation ID, profile, section, assessment status, evidence, gap, impact, audit procedure, and remediation.
6. Aggregate findings by severity, profile, section, and status.
7. Render the final report using `references/report-template.md`.

## Usage

Scan changed Docker/container files:

```text
/scan-container-image
```

Scan a container build directory:

```text
/scan-container-image docker/
```

Scan for CIS Docker Level 2 coverage:

```text
/scan-container-image --level 2
```

Scan Docker Swarm controls:

```text
/scan-container-image --profile swarm
```

## Review Guidance

Prioritize failures that expose the Docker socket, weaken daemon authorization, run privileged containers, disable isolation, use unsafe images, weaken logging/auditing, or allow broad host mounts. Treat `Unknown` as an evidence gap until configuration or command-output proof is provided.
