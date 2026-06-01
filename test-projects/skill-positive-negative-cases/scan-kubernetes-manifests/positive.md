# Positive case: scan-kubernetes-manifests

Expected result: invoke `scan-kubernetes-manifests`.

User request:

```text
/scan-kubernetes-manifests D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture

Run the scan-kubernetes-manifests workflow against the fixture project and generate a Markdown report at D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-kubernetes-manifests\report.md. The report must include rule IDs, evidence paths, severity, remediation, and a no-findings section when applicable.
```

Why this is positive:

- Skill description: Scans Kubernetes manifests, Helm charts, kubeadm/static pod files, kubelet configuration, RBAC, namespaces, network policies, admission controls, and cluster evidence against Kubernetes security benchmark controls. Use when reviewing Kubernetes YAML, cluster hardening, CIS Kubernetes benchmark evidence, pod security, control plane settings, worker node settings, RBAC, service accounts, network policy, or secrets management.
- Uses the explicit trigger `/scan-kubernetes-manifests`.
- Points at known fixture evidence for this skill.

Fixture targets:
- k8s/deployment.yaml

Expected evidence signals:
- privileged: true
- hostNetwork: true
- runAsUser: 0

Expected report output:

- D:\Download\CascadeProjects\secureaiskills\test-projects\skill-positive-negative-cases\scan-kubernetes-manifests\report.md

