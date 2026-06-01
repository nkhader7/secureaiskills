# Negative case: scan-container-image

Expected result: do not invoke `scan-container-image`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-container-image`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-container-image`.

Skill description for comparison:

```text
Scans Dockerfiles, container image build configuration, Docker daemon/runtime configuration, Docker Compose files, Kubernetes container specs, and Docker host evidence against CIS Docker Benchmark v1.8.0 controls and OWASP Docker Top 10. Use when reviewing Docker or container security hardening, container image risks, Docker daemon settings, container runtime flags, Docker Swarm settings, CIS Docker compliance, or OWASP container security.
```
