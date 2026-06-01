# Positive case: scan-container-image

Expected result: invoke `scan-container-image`.

User request:

```text
/scan-container-image D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-container-image workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-container-image\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans Dockerfiles, container image build configuration, Docker daemon/runtime configuration, Docker Compose files, Kubernetes container specs, and Docker host evidence against CIS Docker Benchmark v1.8.0 controls and OWASP Docker Top 10. Use when reviewing Docker or container security hardening, container image risks, Docker daemon settings, container runtime flags, Docker Swarm settings, CIS Docker compliance, or OWASP container security.
- Uses the explicit trigger `/scan-container-image`.
- Points at known fixture evidence for this skill.

Fixture targets:
- Dockerfile
- docker-compose.yml

Expected evidence signals:
- USER root
- privileged: true
- /var/run/docker.sock

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-container-image\report.md

