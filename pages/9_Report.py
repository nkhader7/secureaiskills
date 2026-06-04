"""Page 9 — Final Report: combined scores, executive summary, download."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

FULL_PATH = Path("output/full-report.json")
st.title("Final Report — All Agents")
st.caption("Executive report · Security · Compliance · Coverage · Benchmark · CI/CD · Downloadable JSON.")

report: dict = {}
if FULL_PATH.exists():
    report = json.loads(FULL_PATH.read_text(encoding="utf-8"))

if not report:
    st.info("No full report found. Run all agents from the home page.")
    st.stop()

# Score summary banner
decision = str(report.get("pass_fail_decision", "—")).upper()
risk = str(report.get("overall_risk", "—")).upper()
color = "🟢" if decision == "PASS" else "🔴"
st.subheader(f"{color} Decision: {decision}  |  Risk: {risk}")

cols = st.columns(6)
for col, key, label in zip(cols, [
    "overall_score", "security_score", "compliance_score",
    "validation_score", "coverage_score", "benchmark_score",
], ["Overall", "Security", "Compliance", "Validation", "Coverage", "Benchmark"]):
    col.metric(label, report.get(key, "—"))

tabs = st.tabs(["Executive", "Security", "Compliance", "Coverage", "Benchmarks", "CI/CD", "Download"])

with tabs[0]:
    st.subheader("Executive Report")
    for line in report.get("executive_report", []):
        st.write(f"- {line}")
    summary = report.get("summary", {})
    if summary:
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Skills Analyzed", summary.get("skills_analyzed", "—"))
        col2.metric("Pass/Fail", str(summary.get("pass_fail", "—")).upper())
        col3.metric("Overall Risk", str(summary.get("overall_risk", "—")).upper())

with tabs[1]:
    st.subheader("Security Report")
    for row in report.get("security_report", []):
        risk_col = "🔴" if row.get("overall_risk") == "high" else "🟡" if row.get("overall_risk") == "medium" else "🟢"
        st.write(f"{risk_col} **{row.get('skill', '?')}** — {row.get('overall_risk', '?')}")

with tabs[2]:
    st.subheader("Compliance Report")
    st.dataframe(report.get("compliance_report", []), use_container_width=True)

with tabs[3]:
    st.subheader("Coverage Report")
    st.dataframe(report.get("coverage_report", []), use_container_width=True)
    cmap = report.get("coverage_map", {})
    col1, col2 = st.columns(2)
    col1.write("**Covered domains:**")
    for d in cmap.get("covered_domains", []):
        col1.write(f"  ✓ {d}")
    col2.write("**Missing domains:**")
    for d in cmap.get("missing_domains", []):
        col2.write(f"  ✗ {d}")

with tabs[4]:
    st.subheader("Benchmark Report")
    rows = []
    for r in report.get("benchmark_report", []):
        best = r["formats"][0] if r.get("formats") else {}
        rows.append({"skill": r["skill"], "score": r["benchmark_score"], "best_format": best.get("format", "—")})
    st.dataframe(rows, use_container_width=True)

with tabs[5]:
    st.subheader("CI/CD Report")
    st.dataframe(report.get("ci_cd_report", []), use_container_width=True)
    st.subheader("Recommendations")
    for rec in report.get("recommendations", []):
        st.write(f"- {rec}")

with tabs[6]:
    st.subheader("Download Artifacts")
    st.download_button(
        "Full Report JSON",
        json.dumps(report, indent=2),
        file_name="secureai-full-report.json",
        mime="application/json",
    )
    for name, path in [
        ("Agent 1 Report", Path("output/agent1/agent1-report.json")),
        ("Agent 2 Report", Path("output/agent2/agent2-report.json")),
        ("Agent 3 Report", Path("output/agent3/agent3-report.json")),
        ("Benchmark Report", Path("output/agent3/benchmark-report.json")),
    ]:
        if path.exists():
            st.download_button(
                name,
                path.read_text(encoding="utf-8"),
                file_name=path.name,
                mime="application/json",
                key=f"dl_{path.stem}",
            )
