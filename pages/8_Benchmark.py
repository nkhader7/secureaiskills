"""Page 8 - Benchmarking"""
from __future__ import annotations
import streamlit as st
from pages._shared import inject_theme, sidebar_nav, load_report, score_row, divider, empty_state, stat_block, progress_bar

inject_theme()
sidebar_nav()
st.title("Benchmarking")
st.caption("Token usage, prompt size, parse latency, redundancy, and format efficiency.")

a3 = load_report("agent3")
if not a3:
    empty_state("No benchmark data found.", "⚡")
    st.stop()

bm = a3.get("benchmark_report",[])
if not bm:
    st.info("No benchmark data.")
    st.stop()

avg_score = sum(r.get("benchmark_score",0) for r in bm)/max(len(bm),1)
avg_tokens = sum(r.get("original_prompt_tokens",0) for r in bm)/max(len(bm),1)
top  = max(bm, key=lambda x: x.get("benchmark_score",0), default={})
best_fmt = top.get("ranking",[None])[0] or "—"

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Score",        f"{avg_score:.2f}/10")
c2.metric("Skills",           len(bm))
c3.metric("Avg Prompt Tokens",int(avg_tokens))
c4.metric("Best Format",      best_fmt.upper())
divider()

score_row(
    (avg_score*10, "Avg Score"),
    (max(0,100-(avg_tokens/10000)*100), "Compactness"),
)

tabs = st.tabs(["Leaderboard","Format Rankings","Complexity","Per-Skill"])

with tabs[0]:
    for r in sorted(bm, key=lambda x: x.get("benchmark_score",0), reverse=True):
        best = (r.get("formats",[{}])[0] or {}).get("format","—").upper()
        s    = r.get("benchmark_score",0)
        col  = "#22c55e" if s>=8 else "#f59e0b" if s>=6 else "#ef4444"
        cx   = {"high":"#ef4444","medium":"#f59e0b","low":"#7a90b0"}.get(r.get("execution_complexity","low"),"#7a90b0")
        st.markdown(
            f'<div style="background:rgba(14,21,37,.75);border:1px solid #1e2d44;border-left:3px solid {col};'
            f'border-radius:8px;padding:10px 14px;margin:3px 0;display:flex;justify-content:space-between;align-items:center">'
            f'<div><div style="color:#f1f5fb;font-weight:600;font-size:13px;font-family:monospace">{r["skill"]}</div>'
            f'<div style="color:#7a90b0;font-size:11px">Best: <b style="color:#e2eaf6">{best}</b>'
            f' · Rules: {r.get("rule_count",0)} · Tokens: {r.get("original_prompt_tokens",0):,}'
            f' · <span style="color:{cx}">{r.get("execution_complexity","?").upper()}</span></div></div>'
            f'<div style="color:{col};font-size:22px;font-weight:800;font-family:monospace">{s:.1f}</div></div>',
            unsafe_allow_html=True)

with tabs[1]:
    fmt_scores: dict = {}
    for r in bm:
        for f in r.get("formats",[]):
            fmt_scores.setdefault(f["format"],[]).append(f["format_efficiency_score"])
    for fmt,scores in sorted(fmt_scores.items(), key=lambda x:sum(x[1])/len(x[1]), reverse=True):
        avg = sum(scores)/len(scores)
        col = "#22c55e" if avg>=8 else "#f59e0b" if avg>=6 else "#ef4444"
        st.markdown(progress_bar(avg*10, f"{fmt.upper()} — avg {avg:.2f}/10", col), unsafe_allow_html=True)
    st.caption("JSON consistently ranks highest due to parse speed and compact structure.")

with tabs[2]:
    counts = {"high":0,"medium":0,"low":0}
    for r in bm:
        counts[r.get("execution_complexity","low")] = counts.get(r.get("execution_complexity","low"),0)+1
    st.markdown(stat_block([
        (str(counts["high"]),   "High >100 rules", "#ef4444"),
        (str(counts["medium"]), "Medium 21-100",    "#f59e0b"),
        (str(counts["low"]),    "Low <=20 rules",   "#22c55e"),
    ]), unsafe_allow_html=True)
    lat_rows = sorted(bm, key=lambda x: x.get("estimated_latency_ms",0), reverse=True)[:8]
    divider()
    st.markdown("**Top 8 by Estimated Latency**")
    for r in lat_rows:
        st.markdown(f'<div style="padding:5px 0;font-size:12px">'
                    f'<b style="color:#e2eaf6;font-family:monospace">{r["skill"]}</b>'
                    f'<span style="color:#7a90b0;margin-left:8px">{r.get("estimated_latency_ms",0):.1f} ms</span></div>',
                    unsafe_allow_html=True)

with tabs[3]:
    sel = st.selectbox("Select skill", [r["skill"] for r in bm], key="bm_detail")
    r   = next(x for x in bm if x["skill"]==sel)
    c1,c2 = st.columns(2)
    c1.metric("Score",        r.get("benchmark_score",0))
    c1.metric("Rules",        r.get("rule_count",0))
    c1.metric("Tokens",       r.get("original_prompt_tokens",0))
    best_fmt2 = (r.get("ranking",[None])[0] or "—").upper()
    c2.metric("Best Format",  best_fmt2)
    c2.metric("Complexity",   r.get("execution_complexity","?"))
    c2.metric("Est. Latency", f'{r.get("estimated_latency_ms",0):.1f} ms')
    divider()
    st.dataframe(r.get("formats",[]), use_container_width=True)
