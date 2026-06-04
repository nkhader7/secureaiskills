"""Page 2 — Skill Structure: Agent 1 structural and functional analysis."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A1_PATH = Path("output/agent1/agent1-report.json")
st.title("Skill Structure — Agent 1")
st.caption("Skill Intelligence: discovery, structural analysis, functional validation, execution flow.")

report = st.session_state.get("report") or (
    json.loads(A1_PATH.read_text(encoding="utf-8")) if A1_PATH.exists() else {}
)
a1 = report if report.get("agent") == "agent1" else {}
if not a1:
    full = report
    a1_path = Path("output/agent1/agent1-report.json")
    if a1_path.exists():
        a1 = json.loads(a1_path.read_text(encoding="utf-8"))

if not a1:
    st.info("No Agent 1 report found. Run the analysis from the home page.")
    st.stop()

cr = a1.get("coverage_report", [])
gap = a1.get("gap_analysis", {})
dep = a1.get("dependency_map", {})

# Summary metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Skills", len(cr))
c2.metric("Valid", sum(1 for r in cr if r.get("valid")))
c3.metric("Issues", gap.get("total_issues", 0))
c4.metric("Total Rules", sum(r.get("rules", 0) for r in cr))

tabs = st.tabs(["Coverage Report", "Dependency Map", "Functional Analysis", "Execution Flow", "Recommendations"])

with tabs[0]:
    st.subheader("Coverage Report — all 26 skills")
    st.dataframe(cr, use_container_width=True)
    invalid = [r for r in cr if not r.get("valid")]
    if invalid:
        st.error(f"{len(invalid)} skill(s) failed validation:")
        for r in invalid:
            st.write(f"- **{r['skill']}** — {r.get('issues', 0)} issue(s)")

with tabs[1]:
    st.subheader("Dependency Map")
    if dep:
        for skill, deps in dep.items():
            if deps:
                st.write(f"**{skill}** → {', '.join(str(d) for d in deps)}")
    else:
        st.write("No dependency data available.")

with tabs[2]:
    st.subheader("Functional Analysis (per skill)")
    skills_with_data = [r for r in a1.get("skill_results", []) if "functional" in r]
    if skills_with_data:
        names = [r["skill"] for r in skills_with_data]
        selected = st.selectbox("Select skill", names)
        row = next(r for r in skills_with_data if r["skill"] == selected)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Problem solved:**", row["functional"].get("problem_solved", "—"))
            st.write("**Success criteria:**", row["functional"].get("success_criteria", "—"))
            st.write("**Failure conditions:**")
            for fc in row["functional"].get("failure_conditions", []):
                st.write(f"  - {fc}")
        with col2:
            st.write("**Execution phases:**")
            for ph in row["functional"].get("execution_phases", []):
                st.write(f"  - {ph}")
            st.write("**Data flow:**", row["functional"].get("data_flow_summary", "—"))
            st.write("**Control flow:**", row["functional"].get("control_flow_summary", "—"))
        with st.expander("Validation details"):
            st.json(row.get("validation", {}))
    else:
        st.info("Run Agent 1 to see per-skill functional analysis.")

with tabs[3]:
    st.subheader("Execution Flow")
    for step in a1.get("execution_flow", []):
        st.write(f"→ {step}")

with tabs[4]:
    st.subheader("Recommendations")
    for rec in a1.get("recommendations", []):
        st.write(f"- {rec}")
    st.subheader("Gap Analysis")
    st.json(gap)
