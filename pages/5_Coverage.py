"""Page 5 — Coverage Mapping: security testing domain coverage."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A1_PATH = Path("output/agent1/agent1-report.json")
st.title("Security Testing Coverage — Agent 1")
st.caption("Domain coverage across Threat Modeling, SAST, DAST, SCA, SBOM, IaC, Kubernetes, and more.")

a1: dict = {}
if A1_PATH.exists():
    a1 = json.loads(A1_PATH.read_text(encoding="utf-8"))

if not a1:
    st.info("No Agent 1 report found. Run the analysis from the home page.")
    st.stop()

cmap = a1.get("coverage_map", {})
covered = cmap.get("covered_domains", [])
missing = cmap.get("missing_domains", [])
score = cmap.get("coverage_score", 0)

c1, c2, c3 = st.columns(3)
c1.metric("Coverage Score", f"{round(score * 100, 1)}%" if score <= 1 else f"{score}%")
c2.metric("Covered Domains", len(covered))
c3.metric("Missing Domains", len(missing))

tabs = st.tabs(["Domain Map", "Covered", "Missing & Gaps", "Recommendations"])

with tabs[0]:
    st.subheader("Full Domain Map")
    all_domains = [
        "Threat Modeling", "SAST", "DAST", "SCA", "SBOM",
        "IaC Security", "Kubernetes Security", "Container Security",
        "Secrets Detection", "Dependency Scanning", "Compliance Validation",
        "LLM Security", "Prompt Injection Testing", "Runtime Validation",
        "Exploit Validation", "Remediation", "Reporting", "CI/CD Enforcement", "API Security",
    ]
    rows = []
    for d in all_domains:
        status = "✓ Covered" if d in covered else "✗ Missing"
        rows.append({"Domain": d, "Status": status})
    st.dataframe(rows, use_container_width=True)

with tabs[1]:
    st.subheader("Covered Domains")
    for d in covered:
        st.write(f"✓ {d}")

with tabs[2]:
    st.subheader("Missing Domains")
    if missing:
        for d in missing:
            st.write(f"✗ {d}")
    else:
        st.success("All tracked domains are covered.")
    gap = a1.get("gap_analysis", {})
    if gap.get("validation_issues"):
        st.subheader("Validation Issues")
        for issue in gap["validation_issues"][:20]:
            st.write(f"- {issue}")

with tabs[3]:
    st.subheader("Recommendations")
    for rec in a1.get("recommendations", []):
        st.write(f"- {rec}")
