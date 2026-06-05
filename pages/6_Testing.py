"""Page 6 - Test Generation"""
from __future__ import annotations
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, score_row, panel, divider, empty_state, stat_block

inject_theme()
sidebar_nav()
st.title("Test Generation")
st.caption("Generated test cases: unit, validation, mock LLM, CI/CD, regression, edge cases.")

a3 = load_report("agent3")
if not a3:
    empty_state("No testing report found.", "🧪")
    st.stop()

ci_report  = a3.get("ci_cd_report", [])
cov_report = a3.get("coverage_report", [])
passing    = sum(1 for r in ci_report if r.get("decision")=="pass")
total_cases = sum(r.get("tests",0) for r in cov_report)

c1,c2,c3,c4 = st.columns(4)
c1.metric("CI Pass", f"{passing}/{len(ci_report)}")
c2.metric("Total Test Cases", total_cases)
c3.metric("Skills", len(cov_report))
c4.metric("Pass Rate", f"{round(passing/max(len(ci_report),1)*100)}%")
divider()

score_row(
    (passing/max(len(ci_report),1)*100, "CI Gate"),
    (total_cases/max(len(cov_report),1)/6*100, "Density"),
)

tabs = st.tabs(["Test Case Browser","CI/CD Report","Coverage Report","Test Contract"])

with tabs[0]:
    skill_results = a3.get("skill_results",[])
    if skill_results:
        sel = st.selectbox("Select skill",[r["skill"] for r in skill_results], key="test_skill")
        row = next(r for r in skill_results if r["skill"]==sel)
        tests = row.get("tests",{})
        st.markdown(
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;margin:8px 0">'
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-radius:8px;padding:12px 20px;text-align:center">'
            f'<div style="color:#38bdf8;font-size:24px;font-weight:800;font-family:monospace">{tests.get("case_count",0)}</div>'
            f'<div style="color:#7a90b0;font-size:10px;letter-spacing:1px">CASES</div></div>'
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-radius:8px;padding:12px 20px;text-align:center">'
            f'<div style="color:#22c55e;font-size:24px;font-weight:800;font-family:monospace">{len(tests.get("suites",[]))}</div>'
            f'<div style="color:#7a90b0;font-size:10px;letter-spacing:1px">SUITES</div></div></div>',
            unsafe_allow_html=True)
        severity_filter = st.multiselect("Filter severity",["Critical","High","Medium","Info"],
                                          default=["Critical","High","Medium","Info"], label_visibility="collapsed",
                                          placeholder="Filter by severity…")
        for case in [c for c in tests.get("cases",[]) if c.get("severity") in severity_filter]:
            sev_c = {"Critical":"#dc2626","High":"#ef4444","Medium":"#f59e0b","Info":"#38bdf8"}.get(case.get("severity","Info"),"#7a90b0")
            with st.expander(f'`{case["case_id"]}` — {case["suite"]} / {case["kind"]} — {case["severity"]}'):
                st.markdown(
                    f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">'
                    f'<span style="background:rgba(14,21,37,.8);border:1px solid {sev_c};border-radius:4px;'
                    f'padding:2px 8px;font-size:11px;color:{sev_c}">{case.get("severity","?")}</span>'
                    f'<span style="background:rgba(14,21,37,.8);border:1px solid #1e2d44;border-radius:4px;'
                    f'padding:2px 8px;font-size:11px;color:#7a90b0">{case.get("suite","?")}</span></div>',
                    unsafe_allow_html=True)
                st.write(f"**Rule:** {case.get('rule_id','?')}  |  **Input:** `{case.get('input_file','?')}`")
                st.write(f"**Expected:** {case.get('expected','?')}")
                st.json(case.get("mock_response",{}))
    else:
        st.info("Run test generation to generate test cases.")

with tabs[1]:
    fails = [r for r in ci_report if r.get("decision")=="fail"]
    if fails:
        for r in fails:
            st.markdown(f'<div style="padding:8px 12px;margin:3px 0;background:rgba(239,68,68,.08);'
                        f'border-left:2px solid #ef4444;border-radius:0 6px 6px 0;color:#fca5a5;font-size:13px">'
                        f'✗ <b>{r["skill"]}</b>: {r.get("failure_reasons",[])}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#22c55e;font-size:14px;padding:8px">✓ All skills pass the CI gate</div>',
                    unsafe_allow_html=True)
    st.dataframe(ci_report, use_container_width=True)

with tabs[2]:
    st.dataframe(cov_report, use_container_width=True)

with tabs[3]:
    if skill_results:
        contract = skill_results[0].get("tests",{}).get("validation_contract",[])
        for item in contract:
            st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #1e2d44;font-size:12px">'
                        f'<code style="color:#7dd3fc">{item}</code></div>', unsafe_allow_html=True)
