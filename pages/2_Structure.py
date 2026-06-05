"""Page 2 - Skill Structure"""
from __future__ import annotations

import streamlit as st

from pages._shared import (
    inject_theme, sidebar_nav, load_report, score_row, skill_card, panel,
    divider, empty_state, stat_block,
)

inject_theme()
sidebar_nav()

st.title("Skill Structure")
st.caption("Skill intelligence: discovery, structural analysis, functional validation, dependency mapping.")

a1 = load_report("agent1")
if not a1:
    empty_state("No structure report found.", "🏗️")
    st.stop()

cr  = a1.get("coverage_report", [])
gap = a1.get("gap_analysis", {})
dep = a1.get("dependency_map", {})
cmap = a1.get("coverage_map", {})

valid_count = sum(1 for r in cr if r.get("valid"))
total_rules = sum(r.get("rules", 0) for r in cr)
cov_score   = round(float(cmap.get("coverage_score", 0)) * 100, 1)
issues      = gap.get("total_issues", 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Skills Valid",    f"{valid_count}/{len(cr)}")
c2.metric("Total Rules",     f"{total_rules:,}")
c3.metric("Coverage Score",  f"{cov_score}%")
c4.metric("Issues",          issues)

divider()

tabs = st.tabs(["📋 Roster", "🗺️ Coverage", "🔍 Functional", "⚡ Flow", "🔗 Dependencies", "💡 Recs"])

with tabs[0]:
    score_row(
        (valid_count / max(len(cr), 1) * 100, "Valid"),
        (cov_score, "Coverage"),
        (min(total_rules / 30, 100), "Density"),
    )
    cat_opts = sorted({r.get("category", "Other") for r in cr})
    cat_filter = st.multiselect("Filter by category", cat_opts, default=[], label_visibility="collapsed",
                                placeholder="Filter by category…")
    rows = [r for r in cr if not cat_filter or r.get("category") in cat_filter]
    for row in rows:
        risk = "high" if not row.get("valid") else "low"
        st.markdown(skill_card({
            **row,
            "security_effectiveness_score": min(row.get("rules", 0) / 20 * 100, 100),
            "overall_risk": risk,
            "owasp_coverage_pct": 0,
            "cwe_coverage_pct": 0,
            "rule_quality_score": 100 if row.get("valid") else 45,
            "gaps_count": row.get("issues", 0),
        }), unsafe_allow_html=True)

with tabs[1]:
    covered = cmap.get("covered_domains", [])
    missing = cmap.get("missing_domains", [])
    st.markdown(stat_block([
        (f"{cov_score}%",    "Score",         "#38bdf8"),
        (str(len(covered)),  "Covered",        "#22c55e"),
        (str(len(missing)),  "Missing",        "#ef4444"),
    ]), unsafe_allow_html=True)

    all_domains = [
        "Threat Modeling","SAST","DAST","SCA","SBOM","IaC Security",
        "Kubernetes Security","Container Security","Secrets Detection",
        "Dependency Scanning","Compliance Validation","LLM Security",
        "Prompt Injection Testing","Runtime Validation","Exploit Validation",
        "Remediation","Reporting","CI/CD Enforcement","API Security",
    ]
    col1, col2 = st.columns(2)
    with col1:
        for d in all_domains:
            if d in covered:
                st.markdown(f'✅ <span style="color:#86efac;font-size:13px">{d}</span>', unsafe_allow_html=True)
    with col2:
        for d in all_domains:
            if d not in covered:
                st.markdown(f'❌ <span style="color:#fca5a5;font-size:13px">{d}</span>', unsafe_allow_html=True)

with tabs[2]:
    results = [r for r in a1.get("skill_results", []) if "functional" in r and "skill" in r]
    if results:
        sel = st.selectbox("Select skill", [r["skill"] for r in results], key="struct_func")
        row = next(r for r in results if r["skill"] == sel)
        fn  = row.get("functional", {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(panel("Problem Solved",
                f'<p style="color:#e2eaf6;font-size:13px">{fn.get("problem_solved","—")}</p>'))
            st.markdown(panel("Success Criteria",
                f'<p style="color:#86efac;font-size:13px">{fn.get("success_criteria","—")}</p>', "#22c55e"))
            for fc in fn.get("failure_conditions", []):
                st.markdown(f'<div style="color:#fca5a5;font-size:12px;padding:2px 0">✗ {fc}</div>',
                            unsafe_allow_html=True)
        with col2:
            phases = fn.get("execution_phases", [])
            if phases:
                st.markdown(panel("Phases", "".join(
                    f'<div style="color:#94a3b8;font-size:12px;padding:3px 0">'
                    f'<span style="color:#38bdf8;font-weight:700">{i+1}</span>&nbsp;{p}</div>'
                    for i, p in enumerate(phases)
                )), unsafe_allow_html=True)
            st.markdown(panel("Data Flow",
                f'<p style="color:#7dd3fc;font-size:12px">{fn.get("data_flow_summary","—")}</p>',
                "#7dd3fc"), unsafe_allow_html=True)
        with st.expander("Validation details"):
            st.json(row.get("validation", {}))
    else:
        st.info("Run structure analysis to see per-skill functional details.")

with tabs[3]:
    for i, step in enumerate(a1.get("execution_flow", [])):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0">'
            f'<div style="width:26px;height:26px;border-radius:50%;'
            f'background:rgba(56,189,248,.15);border:1px solid rgba(56,189,248,.4);'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:#38bdf8;font-size:12px;font-weight:700;flex-shrink:0">{i+1}</div>'
            f'<div style="color:#e2eaf6;font-size:13px">{step}</div></div>',
            unsafe_allow_html=True,
        )

with tabs[4]:
    if dep:
        for skill, deps in dep.items():
            if deps:
                refs = "&ensp;→&ensp;".join(
                    f'<code style="font-size:11px;color:#7dd3fc">{d}</code>' for d in deps[:5]
                )
                st.markdown(
                    f'<div style="padding:7px 0;border-bottom:1px solid #1e2d44;font-size:12px">'
                    f'<b style="color:#e2eaf6;font-family:monospace">{skill}</b>&ensp;{refs}</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("No dependency data available.")

with tabs[5]:
    for rec in a1.get("recommendations", []):
        st.markdown(
            f'<div style="padding:8px 12px;margin:4px 0;background:rgba(56,189,248,.06);'
            f'border-left:2px solid #38bdf8;border-radius:0 6px 6px 0;'
            f'color:#94a3b8;font-size:13px">→ {rec}</div>',
            unsafe_allow_html=True,
        )
    if gap.get("validation_issues"):
        divider()
        st.markdown("**Validation Issues**")
        for issue in gap["validation_issues"][:20]:
            st.markdown(f'<div style="color:#fca5a5;font-size:12px;padding:3px 0">⚠ {issue}</div>',
                        unsafe_allow_html=True)
