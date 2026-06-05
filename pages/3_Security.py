"""Page 3 - Security Analysis"""
from __future__ import annotations

import streamlit as st

from pages._shared import (
    inject_theme, sidebar_nav, load_report, badge, risk_badge, score_ring, score_row,
    skill_card, panel, divider, empty_state, finding_item, progress_bar, stat_block,
)

inject_theme()
sidebar_nav()

st.title("Security Analysis")
st.caption("Security review: rule quality, OWASP/CWE coverage, attack-vector completeness.")

a2 = load_report("agent2")
if not a2:
    empty_state("No security report found.", "🔐")
    st.stop()

sr       = a2.get("security_report", [])
cr       = a2.get("compliance_report", [])
rs       = a2.get("risk_summary", {})
findings = a2.get("all_findings", [])
avg_score = a2.get("avg_security_effectiveness_score", 0)

# ── Banner ──
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg Effectiveness", f"{avg_score:.1f}/100")
col2.metric("Overall Risk",      str(a2.get("overall_risk", "—")).upper())
col3.metric("High Risk",         rs.get("high", 0))
col4.metric("Medium Risk",       rs.get("medium", 0))
col5.metric("Total Gaps",        a2.get("total_findings", 0))

divider()

tabs = st.tabs([
    "🛡️ Skill Scores", "📊 OWASP Top 10", "🔢 CWE Coverage",
    "⚠️ Findings", "🔎 Skill Detail",
])

with tabs[0]:
    score_row(
        (100 - rs.get("high", 0) / max(len(sr), 1) * 100, "Security"),
        (sum(r.get("owasp_coverage_pct", 0) for r in sr) / max(len(sr), 1), "OWASP"),
        (sum(r.get("cwe_coverage_pct", 0) for r in sr) / max(len(sr), 1), "CWE"),
        (sum(r.get("rule_quality_score", 0) for r in sr) / max(len(sr), 1), "Quality"),
    )
    divider()
    for row in sorted(sr, key=lambda x: x.get("security_effectiveness_score", 0), reverse=True):
        st.markdown(skill_card(row), unsafe_allow_html=True)

with tabs[1]:
    owasp_agg = a2.get("owasp_top10_aggregate", {})
    if owasp_agg:
        for cat, data in sorted(owasp_agg.items()):
            skills_count = len(data.get("covered_by", []))
            c = "#22c55e" if skills_count >= 2 else "#f59e0b" if skills_count == 1 else "#ef4444"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;'
                f'border-bottom:1px solid #1e2d44">'
                f'<div style="color:{c};font-size:20px;width:24px;flex-shrink:0">'
                f'{"✓" if skills_count else "✗"}</div>'
                f'<div style="flex:1">'
                f'<span style="color:#38bdf8;font-family:monospace;font-size:12px;font-weight:700">{cat}</span>'
                f'<span style="color:#e2eaf6;font-size:13px;margin-left:8px">{data.get("name","")}</span></div>'
                f'<div style="color:#7a90b0;font-size:11px">{skills_count} skill(s)</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(panel("OWASP Gap",
            '<p style="color:#fca5a5;font-size:13px">Most skills lack explicit '
            'owasp_2025_category fields in their rules.<br>'
            'Adding these tags improves traceability and compliance mapping.</p>', "#ef4444"),
            unsafe_allow_html=True)

with tabs[2]:
    total_cwes = a2.get("total_cwes_covered", 0)
    st.markdown(stat_block([
        (str(total_cwes),  "CWEs Tracked",  "#38bdf8"),
        (str(a2.get("skills_analyzed", 0)), "Skills", "#7a90b0"),
    ]), unsafe_allow_html=True)

    for row in sorted(sr, key=lambda x: x.get("cwe_coverage_pct", 0), reverse=True):
        pct = float(row.get("cwe_coverage_pct", 0))
        c   = "#22c55e" if pct >= 75 else "#f59e0b" if pct >= 40 else "#ef4444"
        st.markdown(progress_bar(pct, row.get("skill", "?"), c), unsafe_allow_html=True)

with tabs[3]:
    if findings:
        st.markdown(f'<p style="color:#7a90b0;font-size:12px">{len(findings)} total gaps · showing top 60</p>',
                    unsafe_allow_html=True)
        for f in findings[:60]:
            sev = "high" if "Critical" in f or "missing" in f.lower() else "medium"
            st.markdown(finding_item(f, sev), unsafe_allow_html=True)
        if len(findings) > 60:
            st.caption(f"… and {len(findings) - 60} more. Download report for full list.")
    else:
        st.success("No security gaps detected.")

with tabs[4]:
    valid = [r for r in a2.get("skill_results", []) if "error" not in r and "skill" in r]
    if valid:
        sel = st.selectbox("Select skill", [r["skill"] for r in valid], key="sec_detail")
        row = next(r for r in valid if r["skill"] == sel)

        col1, col2, col3 = st.columns(3)
        score = row.get("security_effectiveness_score", 0)
        col1.metric("Effectiveness", f"{score:.1f}/100")
        col2.metric("Overall Risk",  str(row.get("overall_risk", "—")).upper())
        col3.metric("Gaps",          len(row.get("gaps", [])))

        score_row(
            (row.get("owasp_coverage",{}).get("coverage_pct", 0), "OWASP"),
            (row.get("cwe_coverage",{}).get("coverage_pct", 0),   "CWE"),
            (row.get("attack_vector_coverage",{}).get("coverage_pct", 0), "Vectors"),
            (row.get("rule_quality",{}).get("quality_score", 0),  "Quality"),
        )

        c_left, c_right = st.columns(2)
        with c_left:
            std = row.get("standards_coverage", {})
            st.markdown(panel("Standards Coverage",
                progress_bar(std.get("standards_coverage_pct",0), "Any Standard") +
                f'<div style="color:#7a90b0;font-size:11px;margin-top:6px">'
                f'Primary: <b style="color:#e2eaf6">{std.get("primary_standard","—")}</b> · '
                f'OWASP: {std.get("rules_with_owasp",0)} · '
                f'CWE: {std.get("rules_with_cwe",0)} · '
                f'ASVS: {std.get("rules_with_asvs",0)} · '
                f'CIS: {std.get("rules_with_cis",0)}</div>'
            ), unsafe_allow_html=True)
        with c_right:
            pq = row.get("pattern_quality", {})
            fp_color = {"low":"#22c55e","medium":"#f59e0b","high":"#ef4444"}.get(pq.get("fp_risk","low"),"#7a90b0")
            st.markdown(panel("Pattern Quality",
                f'<div style="color:#7a90b0;font-size:12px">'
                f'Patterns: <b style="color:#e2eaf6">{pq.get("total_patterns",0)}</b> · '
                f'FP Risk: <b style="color:{fp_color}">{pq.get("fp_risk","—").upper()}</b><br>'
                f'Too short: {pq.get("patterns_too_short",0)} · '
                f'No anchors: {pq.get("patterns_no_anchors",0)}</div>'
            ), unsafe_allow_html=True)

        if row.get("gaps"):
            divider()
            st.markdown("**Gaps for this skill**")
            for g in row["gaps"][:12]:
                st.markdown(finding_item(g), unsafe_allow_html=True)

        with st.expander("Full skill detail (JSON)"):
            st.json({k: v for k, v in row.items() if k not in ("llm",)})
