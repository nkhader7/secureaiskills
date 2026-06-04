"""Streamlit multi-agent dashboard for SecureAI Skills analysis."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import streamlit as st

from agents.orchestrator import run_all, DEFAULT_OUTPUT_DIR

REPORT_PATH = DEFAULT_OUTPUT_DIR / "full-report.json"
A1_PATH = DEFAULT_OUTPUT_DIR / "agent1" / "agent1-report.json"
A2_PATH = DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json"
A3_PATH = DEFAULT_OUTPUT_DIR / "agent3" / "agent3-report.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _run(skills: list[str]) -> dict:
    return asyncio.run(run_all(skills=skills or None))


def main() -> None:
    st.set_page_config(page_title="SecureAI Skills — 3-Agent Framework", layout="wide")
    st.title("SecureAI Skills — 3-Agent Analysis Framework")
    st.caption("Agent 1: Intelligence  ·  Agent 2: Security & Governance  ·  Agent 3: Validate & Benchmark")

    with st.sidebar:
        st.header("Run Analysis")
        skill_input = st.text_area("Skills (one per line, blank = all)", height=120)
        skills = [s.strip() for s in skill_input.splitlines() if s.strip()]
        if st.button("Run All Agents", type="primary", use_container_width=True):
            with st.spinner("Running Agent 1, 2, and 3 in parallel…"):
                _run(skills)
            st.success("Analysis complete.")
        if st.button("Run Agent 1 only", use_container_width=True):
            from agents.agent1 import run_agent1
            with st.spinner("Running Agent 1…"):
                asyncio.run(run_agent1(skills=skills or None))
            st.success("Agent 1 done.")
        if st.button("Run Agent 2 only", use_container_width=True):
            from agents.agent2 import run_agent2
            with st.spinner("Running Agent 2…"):
                asyncio.run(run_agent2(skills=skills or None))
            st.success("Agent 2 done.")
        if st.button("Run Agent 3 only", use_container_width=True):
            from agents.agent3 import run_agent3
            with st.spinner("Running Agent 3…"):
                asyncio.run(run_agent3(skills=skills or None))
            st.success("Agent 3 done.")

    full = _load(REPORT_PATH)
    a1 = _load(A1_PATH)
    a2 = _load(A2_PATH)
    a3 = _load(A3_PATH)

    if not full and not a1 and not a2 and not a3:
        st.info("No reports found yet. Run the analysis from the sidebar.")
        return

    if full:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Decision", full.get("pass_fail_decision", "—").upper())
        c2.metric("Skills", full.get("skills_analyzed", "—"))
        c3.metric("Confidence", full.get("confidence", "—"))
        c4.metric("Overall Risk", full.get("overall_risk", "—").upper())
        c5.metric("Coverage", full.get("coverage_map", {}).get("coverage_score", "—"))

    tabs = st.tabs(["Agent 1 — Intelligence", "Agent 2 — Security", "Agent 3 — Benchmark", "Combined", "JSON"])

    with tabs[0]:
        if not a1:
            st.warning("Agent 1 report not found. Run Agent 1 first.")
        else:
            st.subheader("Coverage Map")
            cmap = a1.get("coverage_map", {})
            col1, col2 = st.columns(2)
            col1.metric("Covered Domains", len(cmap.get("covered_domains", [])))
            col2.metric("Missing Domains", len(cmap.get("missing_domains", [])))
            if cmap.get("missing_domains"):
                st.warning("Missing domains: " + ", ".join(cmap["missing_domains"]))
            st.subheader("Skill Coverage Report")
            st.dataframe(a1.get("coverage_report", []), use_container_width=True)
            st.subheader("Gap Analysis")
            gap = a1.get("gap_analysis", {})
            if gap.get("validation_issues"):
                st.error(f"{len(gap['validation_issues'])} validation issues found")
                for issue in gap["validation_issues"][:10]:
                    st.write(f"- {issue}")
            st.subheader("Recommendations")
            for rec in a1.get("recommendations", []):
                st.write(f"- {rec}")

    with tabs[1]:
        if not a2:
            st.warning("Agent 2 report not found. Run Agent 2 first.")
        else:
            risk_counts = a2.get("risk_summary", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("High Risk Skills", risk_counts.get("high", 0), delta_color="inverse")
            c2.metric("Medium Risk Skills", risk_counts.get("medium", 0))
            c3.metric("Low Risk Skills", risk_counts.get("low", 0))
            st.subheader("Security Report")
            st.dataframe(a2.get("security_report", []), use_container_width=True)
            st.subheader("Compliance Report")
            st.dataframe(a2.get("compliance_report", []), use_container_width=True)
            if a2.get("all_findings"):
                st.subheader(f"Findings ({len(a2['all_findings'])})")
                for f in a2["all_findings"][:20]:
                    st.write(f"- {f}")

    with tabs[2]:
        if not a3:
            st.warning("Agent 3 report not found. Run Agent 3 first.")
        else:
            st.subheader("Benchmark Results")
            rows = []
            for skill in a3.get("benchmark_report", []):
                best = skill["formats"][0] if skill.get("formats") else {}
                rows.append({
                    "skill": skill["skill"],
                    "best_format": best.get("format"),
                    "score": skill["benchmark_score"],
                    "complexity": skill["execution_complexity"],
                    "rules": skill["rule_count"],
                })
            st.dataframe(rows, use_container_width=True)
            st.subheader("Test Report")
            st.dataframe(a3.get("coverage_report", []), use_container_width=True)
            st.subheader("CI/CD Report")
            st.dataframe(a3.get("ci_cd_report", []), use_container_width=True)
            st.subheader("Execution Graphs")
            skill_names = sorted(a3.get("graph_artifacts", {}).keys())
            if skill_names:
                selected = st.selectbox("Skill", skill_names)
                st.json(a3["graph_artifacts"][selected])

    with tabs[3]:
        if full:
            st.subheader("Executive Report")
            for line in full.get("executive_report", []):
                st.write(line)
            st.subheader("Combined Recommendations")
            for rec in full.get("recommendations", []):
                st.write(f"- {rec}")
        else:
            st.info("Run all agents to generate the combined report.")

    with tabs[4]:
        active = full or a1 or a2 or a3
        if active:
            label = "full-report.json" if full else ("agent1-report.json" if a1 else ("agent2-report.json" if a2 else "agent3-report.json"))
            st.download_button(f"Download {label}", json.dumps(active, indent=2), label)
            st.json(active)


if __name__ == "__main__":
    main()
