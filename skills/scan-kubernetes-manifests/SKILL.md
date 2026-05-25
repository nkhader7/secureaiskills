---
name: scan-kubernetes-manifests
description: Scans Kubernetes manifests, Helm charts, kubeadm/static pod files, kubelet configuration, RBAC, namespaces, network policies, admission controls, and cluster evidence against Kubernetes security benchmark controls. Use when reviewing Kubernetes YAML, cluster hardening, CIS Kubernetes benchmark evidence, pod security, control plane settings, worker node settings, RBAC, service accounts, network policy, or secrets management.
triggers:
  - /scan-kubernetes-manifests
  - "scan.*kubernetes"
  - "scan.*k8s"
  - "kubernetes.*benchmark"
  - "cis.*kubernetes"
  - "k8s.*security"
references:
  rules: references/rules.yaml
  report_template: references/report-template.md
  base_report: ../_shared/base-report.md
---

# scan-kubernetes-manifests

Scans Kubernetes manifests, control-plane evidence, worker-node evidence, RBAC, policy, and workload configuration against Kubernetes hardening controls.

## Orchestration

1. Load `references/rules.yaml` to get the active Kubernetes benchmark control set.
2. Identify target evidence:
   - Default to changed Kubernetes files on the current branch.
   - Include `*.yaml`, `*.yml`, Helm templates, Kustomize overlays, kubeadm config, static pod manifests, RBAC manifests, admission policy, network policies, Pod Security Admission labels, kubelet config, and command output when provided.
   - Scan a user-provided path when one is supplied.
3. Determine scope:
   - Include control plane checks when API server, controller manager, scheduler, etcd, or kubeadm evidence exists.
   - Include worker node checks when kubelet, kube-proxy, node config, or workload evidence exists.
   - Include policy checks when RBAC, service accounts, namespaces, network policy, pod security, or secrets management is in scope.
4. Evaluate each rule using `match_strategy: cis_kubernetes_review`.
   - For `assessment_status: Automated`, look for direct manifest, config, or command-output evidence.
   - For `assessment_status: Manual`, evaluate design and operational evidence and mark unclear controls as review findings.
   - Mark controls `Pass`, `Fail`, `Partial`, `Unknown`, or `Not Applicable`.
5. Capture recommendation ID, profile, section, assessment status, evidence, gap, impact, audit procedure, and remediation.
6. Aggregate findings by severity, profile, section, and status.
7. Render the final report using `references/report-template.md`.

## Usage

Scan changed Kubernetes manifests:

```text
/scan-kubernetes-manifests
```

Scan a Kubernetes manifest directory:

```text
/scan-kubernetes-manifests k8s/
```

Scan Helm charts:

```text
/scan-kubernetes-manifests charts/
```

Scan cluster evidence:

```text
/scan-kubernetes-manifests evidence/kubernetes/
```

## Review Guidance

Prioritize failures that weaken API server authentication, RBAC, etcd protection, kubelet authorization, privileged workloads, host namespace sharing, hostPath mounts, service account token use, network policy, or secrets handling. Treat `Unknown` as an evidence gap until configuration or command-output proof is provided.
