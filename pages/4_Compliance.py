"""Page 4 - Compliance Analysis"""
from __future__ import annotations
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, score_row, divider, empty_state, stat_block

inject_theme()
sidebar_nav()
st.title("Compliance Analysis")
st.caption("NIST AI RMF · OWASP ASVS 5.0 · SLSA · OWASP LLM Top 10 · CIS Controls.")

a2 = load_report("agent2")
if not a2:
    empty_state("No compliance report found.", "📜")
    st.stop()

cr = a2.get("compliance_report", [])
if not cr:
    st.info("No compliance data. Run compliance analysis.")
    st.stop()

avg_score = round(sum(r.get("compliance_score", 0) for r in cr) / max(len(cr), 1), 1)
all_pass  = sum(1 for r in cr if r.get("governance_valid"))
slsa_dist = {1:0,2:0,3:0,4:0}
for r in cr:
    slsa_dist[min(r.get("slsa_level",1),4)] += 1

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Compliance Score", f"{avg_score:.1f}")
c2.metric("Governance Valid", f"{all_pass}/{len(cr)}")
c3.metric("SLSA >= L2", sum(v for lv,v in slsa_dist.items() if lv>=2))
c4.metric("OWASP LLM Pass", sum(1 for r in cr if r.get("owasp_llm_top10_pass")))
divider()

tabs = st.tabs(["Compliance Scores","NIST AI RMF","SLSA Levels","ASVS Chapters","Recommendations"])

with tabs[0]:
    for row in sorted(cr, key=lambda x: x.get("compliance_score",0), reverse=True):
        s = float(row.get("compliance_score",0))
        slsa = row.get("slsa_level",1)
        gov  = row.get("governance_valid",False)
        c  = "#22c55e" if s>=75 else "#f59e0b" if s>=50 else "#ef4444"
        gc = "#22c55e" if gov else "#ef4444"
        st.markdown(
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-left:3px solid {c};'
            f'border-radius:8px;padding:10px 14px;margin:3px 0;display:flex;align-items:center;justify-content:space-between">'
            f'<div><div style="color:#f1f5fb;font-weight:600;font-size:13px;font-family:monospace">{row.get("skill","?")}</div>'
            f'<div style="color:#7a90b0;font-size:11px">Gov: <b style="color:{gc}">{"Valid" if gov else "Review"}</b> SLSA L{slsa}</div></div>'
            f'<div style="color:{c};font-size:22px;font-weight:800;font-family:monospace">{s:.0f}</div></div>',
            unsafe_allow_html=True)

with tabs[1]:
    nd = {"GOVERN":"Policy & risk mgmt","MAP":"Categorise risks","MEASURE":"Analyse AI risks","MANAGE":"Prioritise risks"}
    for func in ["GOVERN","MAP","MEASURE","MANAGE"]:
        pc = sum(1 for r in cr if r.get("nist_ai_rmf",{}).get(func)=="pass")
        pct = pc/max(len(cr),1)*100
        col = "#22c55e" if pct>=80 else "#f59e0b" if pct>=50 else "#ef4444"
        st.markdown(
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-radius:8px;padding:12px 16px;margin:6px 0">'
            f'<div style="display:flex;justify-content:space-between">'
            f'<div><span style="color:{col};font-family:monospace;font-size:14px;font-weight:700">{func}</span>'
            f'<span style="color:#7a90b0;font-size:12px;margin-left:10px">{nd.get(func,"")}</span></div>'
            f'<span style="color:{col};font-weight:700">{pc}/{len(cr)}</span></div>'
            f'<div style="background:#1e2d44;border-radius:4px;height:4px;margin-top:8px">'
            f'<div style="background:{col};border-radius:4px;height:4px;width:{pct:.0f}%"></div></div></div>',
            unsafe_allow_html=True)

with tabs[2]:
    sc = {1:"#7a90b0",2:"#38bdf8",3:"#22c55e",4:"#a78bfa"}
    sd = {1:"Documentation",2:"Versioned+governance",3:"OWASP+CWE",4:"Full traceability"}
    for level in [4,3,2,1]:
        count = slsa_dist.get(level,0)
        color = sc[level]
        names = ", ".join(r["skill"] for r in cr if r.get("slsa_level",1)==level)[:80]
        st.markdown(
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-left:3px solid {color};'
            f'border-radius:8px;padding:12px 16px;margin:4px 0">'
            f'<div style="display:flex;justify-content:space-between">'
            f'<div><span style="color:{color};font-weight:700;font-size:14px;font-family:monospace">SLSA L{level}</span>'
            f'<span style="color:#7a90b0;font-size:12px;margin-left:10px">{sd[level]}</span></div>'
            f'<span style="color:{color};font-weight:700">{count}</span></div>'
            + (f'<div style="color:#7a90b0;font-size:11px;margin-top:6px">{names}</div>' if names else "")
            + "</div>",
            unsafe_allow_html=True)

with tabs[3]:
    cs: dict = {}
    for r in cr:
        for ch in r.get("asvs_chapters",[]):
            cs.setdefault(ch,[]).append(r["skill"])
    if cs:
        for ch in sorted(cs):
            st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #1e2d44;font-size:12px">'
                        f'<b style="color:#38bdf8;font-family:monospace">{ch}</b>'
                        f' &ensp;<span style="color:#7a90b0">{' · '.join(cs[ch][:5])}</span></div>',
                        unsafe_allow_html=True)
    else:
        st.info("No ASVS chapter data.")

with tabs[4]:
    for rec in a2.get("recommendations",[]):
        st.markdown(f'<div style="padding:8px 12px;margin:4px 0;background:rgba(56,189,248,.06);'
                    f'border-left:2px solid #38bdf8;border-radius:0 6px 6px 0;color:#94a3b8;font-size:13px">→ {rec}</div>',
                    unsafe_allow_html=True)
