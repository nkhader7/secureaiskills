from __future__ import annotations

import asyncio
import json
from pathlib import Path

import streamlit as st

from agent3 import DEFAULT_OUTPUT_DIR, run_agent3


REPORT_PATH = Path(DEFAULT_OUTPUT_DIR) / "agent3-report.json"


def load_report() -> dict:
    if not REPORT_PATH.exists():
        return {}
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="SecureAI Agent 3", layout="wide")
    st.title("SecureAI Agent 3")
    st.caption("Testing, conversion, benchmarking, graphs, reporting, and CI/CD output.")

    if st.sidebar.button("Run Agent 3", type="primary", use_container_width=True):
        with st.spinner("Running Agent 3..."):
            asyncio.run(run_agent3(output_dir=str(DEFAULT_OUTPUT_DIR)))
        st.success("Agent 3 artifacts generated.")

    report = load_report()
    if not report:
        st.warning("No Agent 3 report found yet.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Decision", report["pass_fail_decision"])
    c2.metric("Skills", report["skills_analyzed"])
    c3.metric("Confidence", report["confidence"])
    c4.metric("CI Reports", len(report["ci_cd_report"]))

    tabs = st.tabs(["Executive", "Benchmarks", "Tests", "CI/CD", "Graphs", "JSON"])
    with tabs[0]:
        for line in report["executive_report"]:
            st.write(line)
    with tabs[1]:
        rows = []
        for skill in report["benchmark_report"]:
            best = skill["formats"][0] if skill.get("formats") else {}
            rows.append({"skill": skill["skill"], "best_format": best.get("format"), "score": skill["benchmark_score"]})
        st.dataframe(rows, use_container_width=True)
    with tabs[2]:
        st.dataframe(report["coverage_report"], use_container_width=True)
    with tabs[3]:
        st.dataframe(report["ci_cd_report"], use_container_width=True)
    with tabs[4]:
        skill_names = sorted(report["graph_artifacts"])
        selected = st.selectbox("Skill", skill_names)
        st.json(report["graph_artifacts"][selected])
    with tabs[5]:
        st.download_button("Download agent3-report.json", json.dumps(report, indent=2), "agent3-report.json")
        st.json(report)


if __name__ == "__main__":
    main()
