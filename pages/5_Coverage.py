"""Page 5 - Coverage Mapping"""
from __future__ import annotations
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, score_row, divider, empty_state, stat_block

inject_theme()
sidebar_nav()
st.title("Security Testing Coverage")
st.caption("Domain coverage across Threat Modeling, SAST, DAST, SCA, SBOM, IaC, Kubernetes, and more.")

a1 = load_report("agent1")
if not a1:
    empty_state("No coverage data found.", "🗺")
    st.stop()

cmap      = a1.get("coverage_map", {})
covered   = cmap.get("covered_domains", [])
missing   = cmap.get("missing_domains", [])
score     = float(cmap.get("coverage_score", 0))
score_pct = round(score * 100, 1) if score <= 1 else score

c1, c2, c3 = st.columns(3)
c1.metric("Coverage Score", f"{score_pct}%")
c2.metric("Covered Domains", len(covered))
c3.metric("Missing Domains", len(missing))
divider()

score_row(
    (score_pct, "Coverage"),
    (len(covered) / 19 * 100, "Domains"),
    (0 if missing else 100, "Complete"),
)

all_domains = ["Threat Modeling","SAST","DAST","SCA","SBOM","IaC Security",
    "Kubernetes Security","Container Security","Secrets Detection","Dependency Scanning",
    "Compliance Validation","LLM Security","Prompt Injection Testing","Runtime Validation",
    "Exploit Validation","Remediation","Reporting","CI/CD Enforcement","API Security"]

tabs = st.tabs(["Domain Map", "Gap Analysis", "Recommendations"])

with tabs[0]:
    st.markdown(stat_block([
        (f"{score_pct}%", "Score",   "#38bdf8"),
        (str(len(covered)), "Covered", "#22c55e"),
        (str(len(missing)), "Missing", "#ef4444"),
    ]), unsafe_allow_html=True)
    divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Covered Domains**")
        for d in all_domains:
            if d in covered:
                st.markdown(f'<div style="padding:5px 0;font-size:13px"><span style="color:#22c55e">✓</span><span style="color:#86efac;margin-left:8px">{d}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Missing Domains**")
        for d in all_domains:
            if d not in covered:
                st.markdown(f'<div style="padding:5px 0;font-size:13px"><span style="color:#ef4444">✗</span><span style="color:#fca5a5;margin-left:8px">{d}</span></div>', unsafe_allow_html=True)

with tabs[1]:
    gap = a1.get("gap_analysis", {})
    for issue in gap.get("validation_issues", [])[:20]:
        st.markdown(f'<div style="color:#fca5a5;font-size:12px;padding:3px 0">⚠ {issue}</div>', unsafe_allow_html=True)
    for d in missing:
        st.markdown(f'<div style="padding:8px 12px;margin:3px 0;background:rgba(239,68,68,.06);border-left:2px solid #ef4444;border-radius:0 6px 6px 0;color:#fca5a5;font-size:13px">✗ {d}</div>', unsafe_allow_html=True)

with tabs[2]:
    for rec in a1.get("recommendations", []):
        st.markdown(f'<div style="padding:8px 12px;margin:4px 0;background:rgba(56,189,248,.06);border-left:2px solid #38bdf8;border-radius:0 6px 6px 0;color:#94a3b8;font-size:13px">→ {rec}</div>', unsafe_allow_html=True)
