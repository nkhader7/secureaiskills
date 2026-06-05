"""Page 7 - Skill Conversion"""
from __future__ import annotations
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, divider, empty_state, progress_bar

inject_theme()
sidebar_nav()
st.title("Skill Conversion")
st.caption("Converted formats: Markdown, YAML, TOML, JSON, and Python. Intent and security constraints preserved.")

a3 = load_report("agent3")
if not a3:
    empty_state("No conversion report found.", "🔄")
    st.stop()

skill_results = a3.get("skill_results",[])
if not skill_results:
    st.info("No skill results.")
    st.stop()

names = [r["skill"] for r in skill_results]
sel   = st.selectbox("Select skill", names)
row   = next(r for r in skill_results if r["skill"]==sel)
convs = row.get("conversions",{})

FORMATS = ["markdown","yaml","toml","json","python"]
EXTS    = {"markdown":"md","yaml":"yaml","toml":"toml","json":"json","python":"py"}

fmt_tabs = st.tabs([f.upper() for f in FORMATS] + ["Size Comparison"])

for i, fmt in enumerate(FORMATS):
    with fmt_tabs[i]:
        item = convs.get(fmt,{})
        if not item:
            st.info("No conversion available.")
            continue
        c1,c2,c3 = st.columns(3)
        c1.metric("Bytes",           item.get("bytes",0))
        c2.metric("Est. Tokens",     item.get("tokens_estimate",0))
        c3.metric("Preserved Fields",len(item.get("preserves",[])))
        content = item.get("content","")
        st.code(content[:3000] + ("\n…" if len(content)>3000 else ""),
                language=fmt if fmt!="markdown" else "markdown")
        ext = EXTS.get(fmt,fmt)
        st.download_button(f"⬇ Download {fmt.upper()}", content,
                           file_name=f"{sel}.{ext}", mime="text/plain", key=f"dl_{sel}_{fmt}")

with fmt_tabs[-1]:
    st.subheader("Format Size Comparison")
    bm_formats = row.get("benchmark",{}).get("formats",[])
    score_map = {r["format"]:r.get("format_efficiency_score",0) for r in bm_formats}
    for fmt in FORMATS:
        item  = convs.get(fmt,{})
        tok   = item.get("tokens_estimate",0)
        score = score_map.get(fmt,0)
        max_tok = max(convs[f].get("tokens_estimate",1) for f in FORMATS if f in convs) or 1
        c = "#22c55e" if score>=8 else "#f59e0b" if score>=6 else "#ef4444"
        st.markdown(progress_bar(tok/max_tok*100, f"{fmt.upper()} — {tok:,} tokens  ·  Score {score:.1f}/10", c),
                    unsafe_allow_html=True)
    ranking = row.get("benchmark",{}).get("ranking",[])
    if ranking:
        st.markdown(f'<div style="color:#22c55e;font-size:13px;margin-top:8px">✓ Best format: <b>{ranking[0].upper()}</b></div>',
                    unsafe_allow_html=True)
