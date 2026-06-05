"""Page 9 — Final Report"""
from __future__ import annotations
import json
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, badge, risk_badge, score_row, divider, empty_state, stat_block

inject_theme()
sidebar_nav()
st.title("Final Report")
st.caption("Executive summary, validation scores, CI/CD gate, and downloadable JSON.")

full = load_report("full")
if not full:
    empty_state("No full report found. Run validation.", "📋")
    st.stop()

decision = str(full.get("pass_fail_decision","?")).upper()
risk     = str(full.get("overall_risk","?")).upper()
badge_d  = '🟢' if decision=="PASS" else '🔴'
risk_c   = {"LOW":"#22c55e","MEDIUM":"#f59e0b","HIGH":"#ef4444"}.get(risk,"#7a90b0")

st.markdown(
    f'<div style="background:rgba(14,21,37,.85);border:1px solid #1e2d44;border-radius:10px;'
    f'padding:20px 24px;margin:8px 0">'
    f'<div style="display:flex;align-items:center;gap:16px">'
    f'<div style="font-size:40px">{badge_d}</div>'
    f'<div>'
    f'<div style="color:#f1f5fb;font-size:22px;font-weight:800">{decision}</div>'
    f'<div style="color:{risk_c};font-size:14px;font-weight:600;margin-top:2px">{risk} RISK</div>'
    f'</div>'
    f'<div style="margin-left:auto;text-align:right">'
    f'<div style="color:#38bdf8;font-size:36px;font-weight:800;font-family:monospace">{full.get("overall_score","?")}</div>'
    f'<div style="color:#7a90b0;font-size:10px;letter-spacing:1.2px">OVERALL SCORE</div></div></div></div>',
    unsafe_allow_html=True)

score_row(
    (float(full.get("security_score",0)),    "Security"),
    (float(full.get("compliance_score",0)),  "Compliance"),
    (float(full.get("validation_score",0)),  "Validation"),
    (float(full.get("coverage_score",0)),    "Coverage"),
    (float(full.get("benchmark_score",0)),   "Benchmark"),
)
divider()

tabs = st.tabs(["Executive","Security","Compliance","Coverage","CI/CD","Download"])

with tabs[0]:
    for line in full.get("executive_report",[]):
        st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #1e2d44;color:#e2eaf6;font-size:13px">{line}</div>',
                    unsafe_allow_html=True)
    summary = full.get("summary",{})
    if summary:
        divider()
        st.markdown(stat_block([
            (str(summary.get("skills_analyzed","?")), "Skills",      "#38bdf8"),
            (str(summary.get("pass_fail","?")),        "Decision",    "#22c55e" if summary.get("pass_fail","")=="pass" else "#ef4444"),
            (str(summary.get("overall_risk","?")),     "Risk",        risk_c),
            (str(summary.get("overall_score","?")),    "Score",       "#38bdf8"),
        ]), unsafe_allow_html=True)

with tabs[1]:
    for row in full.get("security_report",[]):
        rc = {"high":"#ef4444","medium":"#f59e0b","low":"#22c55e"}.get(row.get("overall_risk","low"),"#7a90b0")
        st.markdown(
            f'<div style="padding:6px 0;border-bottom:1px solid #1e2d44;display:flex;align-items:center;gap:10px">'
            f'<span style="width:8px;height:8px;border-radius:50%;background:{rc};display:inline-block;flex-shrink:0"></span>'
            f'<span style="color:#f1f5fb;font-family:monospace;font-size:13px">{row.get("skill","?")}</span>'
            f'<span style="color:{rc};font-size:11px;margin-left:auto">{str(row.get("overall_risk","?")).upper()}</span></div>',
            unsafe_allow_html=True)

with tabs[2]:
    st.dataframe(full.get("compliance_report",[]), use_container_width=True)

with tabs[3]:
    cmap = full.get("coverage_map",{})
    col1,col2 = st.columns(2)
    with col1:
        for d in cmap.get("covered_domains",[]):
            st.markdown(f'<div style="color:#86efac;font-size:13px;padding:3px 0">✓ {d}</div>', unsafe_allow_html=True)
    with col2:
        for d in cmap.get("missing_domains",[]):
            st.markdown(f'<div style="color:#fca5a5;font-size:13px;padding:3px 0">✗ {d}</div>', unsafe_allow_html=True)

with tabs[4]:
    ci = full.get("ci_cd_report",[])
    passing = sum(1 for r in ci if r.get("decision")=="pass")
    st.markdown(
        f'<div style="color:{"#22c55e" if passing==len(ci) else "#f59e0b"};font-size:14px;margin-bottom:8px">'
        f'{"✓ All" if passing==len(ci) else f"⚠ {passing}/{len(ci)}"} skills pass CI gate</div>',
        unsafe_allow_html=True)
    st.dataframe(ci, use_container_width=True)
    divider()
    for rec in full.get("recommendations",[]):
        st.markdown(f'<div style="padding:7px 12px;margin:3px 0;background:rgba(56,189,248,.06);'
                    f'border-left:2px solid #38bdf8;border-radius:0 6px 6px 0;color:#94a3b8;font-size:13px">→ {rec}</div>',
                    unsafe_allow_html=True)

with tabs[5]:
    st.download_button("⬇ Full Report JSON", json.dumps(full,indent=2),
                       file_name="secureai-full-report.json", mime="application/json",
                       use_container_width=True)
    divider()
    for name, agent in [("Structure Report","agent1"),("Security & Compliance Report","agent2"),
                        ("Operational Readiness Report","agent3")]:
        r = load_report(agent)
        if r:
            st.download_button(f"⬇ {name}", json.dumps(r,indent=2),
                               file_name=f"secureai-{agent}-report.json", mime="application/json",
                               key=f"dl_{agent}")
