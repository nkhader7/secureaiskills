"""Page 6 — Test Generation: Agent 3 test cases, suites, and CI/CD gates."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A3_PATH = Path("output/agent3/agent3-report.json")
st.title("Test Generation — Agent 3")
st.caption("Generated test cases: unit, validation, mock LLM, CI/CD, regression, edge cases.")

a3: dict = {}
if A3_PATH.exists():
    a3 = json.loads(A3_PATH.read_text(encoding="utf-8"))

if not a3:
    st.info("No Agent 3 report found. Run the analysis from the home page.")
    st.stop()

ci_report = a3.get("ci_cd_report", [])
cov_report = a3.get("coverage_report", [])

passing = sum(1 for r in ci_report if r.get("decision") == "pass")
total_tests = sum(r.get("tests", 0) for r in cov_report)

c1, c2, c3, c4 = st.columns(4)
c1.metric("CI Pass", f"{passing}/{len(ci_report)}")
c2.metric("Total Test Cases", total_tests)
c3.metric("Skills", len(cov_report))
c4.metric("Pass Rate", f"{round(passing / max(len(ci_report), 1) * 100)}%")

tabs = st.tabs(["Test Case Browser", "CI/CD Report", "Coverage Report", "Test Contract"])

with tabs[0]:
    st.subheader("Generated Test Cases")
    skill_results = a3.get("skill_results", [])
    if skill_results:
        names = [r["skill"] for r in skill_results]
        selected = st.selectbox("Select skill", names)
        row = next(r for r in skill_results if r["skill"] == selected)
        tests = row.get("tests", {})
        st.write(f"**Test project:** `{tests.get('project_name', '—')}`")
        st.write(f"**Suites:** {', '.join(tests.get('suites', []))}")
        st.write(f"**Cases:** {tests.get('case_count', 0)}")
        severity_filter = st.multiselect(
            "Filter by severity",
            ["Critical", "High", "Medium", "Info"],
            default=["Critical", "High", "Medium", "Info"],
        )
        cases = [c for c in tests.get("cases", []) if c.get("severity") in severity_filter]
        for case in cases:
            with st.expander(f"`{case['case_id']}` — {case['suite']} / {case['kind']} — {case['severity']}"):
                st.write(f"**Rule:** {case['rule_id']}  |  **Input:** `{case['input_file']}`")
                st.write(f"**Expected:** {case['expected']}")
                st.json(case["mock_response"])

with tabs[1]:
    st.subheader("CI/CD Report")
    fail_rows = [r for r in ci_report if r.get("decision") == "fail"]
    if fail_rows:
        st.warning(f"{len(fail_rows)} skill(s) failed CI gate:")
        for r in fail_rows:
            st.write(f"- **{r['skill']}**: {r.get('failure_reasons', [])}")
    else:
        st.success("All skills passed the CI gate.")
    st.dataframe(ci_report, use_container_width=True)

with tabs[2]:
    st.subheader("Coverage Report")
    st.dataframe(cov_report, use_container_width=True)

with tabs[3]:
    st.subheader("Validation Contract")
    if skill_results:
        contract = skill_results[0].get("tests", {}).get("validation_contract", [])
        for item in contract:
            st.write(f"- `{item}`")
