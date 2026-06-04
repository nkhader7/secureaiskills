from __future__ import annotations

import asyncio
import json
from pathlib import Path

import streamlit as st

from common import DEFAULT_OUTPUT_DIR
from orchestrator import MISSION_STATEMENT, run_framework


REPORT_PATH = Path(DEFAULT_OUTPUT_DIR) / "final-orchestrator-report.json"


def load_report() -> dict:
    if not REPORT_PATH.exists():
        return {}
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="AI Skill Governance", layout="wide")
    st.title("AI Skill Analysis and Governance Framework")
    st.caption(MISSION_STATEMENT)

    if st.sidebar.button("Run 3-Agent Assessment", type="primary", use_container_width=True):
        with st.spinner("Running agents in parallel..."):
            asyncio.run(run_framework(output_dir=str(DEFAULT_OUTPUT_DIR)))
        st.success("Framework reports generated.")

    report = load_report()
    if not report:
        st.warning("No final orchestrator report found yet.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Decision", report["pass_fail_decision"])
    c2.metric("Skills", report["skills_analyzed"])
    c3.metric("Confidence", report["confidence"])
    c4.metric("Recommendations", len(report["recommendations"]))

    tabs = st.tabs(["Executive", "Security", "Compliance", "Coverage", "Benchmarks", "Tests", "CI/CD", "Graphs", "JSON"])
    with tabs[0]:
        st.json(report["executive_report"])
        st.write("Recommendations")
        st.write(report["recommendations"])
    with tabs[1]:
        st.json(report["security_report"])
    with tabs[2]:
        st.json(report["compliance_report"])
    with tabs[3]:
        st.dataframe(report["coverage_report"], use_container_width=True)
    with tabs[4]:
        rows = []
        for item in report["benchmark_report"]:
            best = item["formats"][0] if item.get("formats") else {}
            rows.append({"skill": item["skill"], "best_format": best.get("format"), "benchmark_score": item["benchmark_score"]})
        st.dataframe(rows, use_container_width=True)
    with tabs[5]:
        st.json(report["test_report"])
    with tabs[6]:
        st.json(report["ci_cd_report"])
    with tabs[7]:
        skill_names = sorted(report["graph_artifacts"])
        selected = st.selectbox("Skill", skill_names)
        st.json(report["graph_artifacts"][selected])
    with tabs[8]:
        st.download_button("Download final-orchestrator-report.json", json.dumps(report, indent=2), "final-orchestrator-report.json")
        st.json(report)


if __name__ == "__main__":
    main()
