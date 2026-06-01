# Negative case: scan-kubernetes-manifests

Expected result: do not invoke `scan-kubernetes-manifests`.

User request:

```text
Review the wording in README.md for clarity and grammar. Do not perform a security scan, audit, threat model, dependency inventory, SBOM generation, or compliance review.
```

Why this is negative:

- It does not use the trigger `/scan-kubernetes-manifests`.
- It asks for editorial feedback only.
- It explicitly excludes the security workflow covered by `scan-kubernetes-manifests`.

Skill description for comparison:

```text
Scans Kubernetes manifests, Helm charts, kubeadm/static pod files, kubelet configuration, RBAC, namespaces, network policies, admission controls, and cluster evidence against Kubernetes security benchmark controls. Use when reviewing Kubernetes YAML, cluster hardening, CIS Kubernetes benchmark evidence, pod security, control plane settings, worker node settings, RBAC, service accounts, network policy, or secrets management.
```
