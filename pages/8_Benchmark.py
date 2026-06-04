"""Page 8 — Benchmarking: token efficiency, format comparison, latency estimates."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A3_PATH = Path("output/agent3/agent3-report.json")
st.title("Benchmarking — Agent 3")
st.caption("Token usage · Prompt size · Parse latency · Redundancy · Format efficiency rankings.")

a3: dict = {}
if A3_PATH.exists():
    a3 = json.loads(A3_PATH.read_text(encoding="utf-8"))

if not a3:
    st.info("No Agent 3 report found. Run the analysis from the home page.")
    st.stop()

bm_report = a3.get("benchmark_report", [])
if not bm_report:
    st.info("No benchmark data available.")
    st.stop()

tabs = st.tabs(["Summary", "Top Skills", "Format Rankings", "Latency & Complexity", "Per-Skill Detail"])

with tabs[0]:
    avg_score = sum(r.get("benchmark_score", 0) for r in bm_report) / len(bm_report)
    avg_tokens = sum(r.get("original_prompt_tokens", 0) for r in bm_report) / len(bm_report)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Benchmark Score", f"{avg_score:.2f}/10")
    c2.metric("Skills Benchmarked", len(bm_report))
    c3.metric("Avg Prompt Tokens", int(avg_tokens))
    c4.metric("Best Format", bm_report[0]["ranking"][0].upper() if bm_report and bm_report[0].get("ranking") else "—")

with tabs[1]:
    st.subheader("Top Skills by Benchmark Score")
    top = sorted(bm_report, key=lambda r: r.get("benchmark_score", 0), reverse=True)
    rows = []
    for r in top:
        best = r["formats"][0] if r.get("formats") else {}
        rows.append({
            "skill": r["skill"],
            "score": r["benchmark_score"],
            "best_format": best.get("format", "—").upper(),
            "complexity": r["execution_complexity"],
            "rules": r["rule_count"],
            "tokens": r["original_prompt_tokens"],
        })
    st.dataframe(rows, use_container_width=True)

with tabs[2]:
    st.subheader("Format Efficiency Rankings")
    format_scores: dict[str, list[float]] = {}
    for r in bm_report:
        for f in r.get("formats", []):
            fmt = f["format"]
            format_scores.setdefault(fmt, []).append(f["format_efficiency_score"])
    rows2 = [
        {"Format": fmt.upper(), "Avg Efficiency Score": round(sum(scores) / len(scores), 2), "Skills": len(scores)}
        for fmt, scores in sorted(format_scores.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
    ]
    st.dataframe(rows2, use_container_width=True)
    st.caption("JSON consistently ranks highest due to parse speed and structure score.")

with tabs[3]:
    st.subheader("Execution Complexity")
    complexity_counts = {"high": 0, "medium": 0, "low": 0}
    for r in bm_report:
        complexity_counts[r.get("execution_complexity", "low")] += 1
    st.write(f"**High complexity:** {complexity_counts['high']} skills (>100 rules)")
    st.write(f"**Medium complexity:** {complexity_counts['medium']} skills (21–100 rules)")
    st.write(f"**Low complexity:** {complexity_counts['low']} skills (≤20 rules)")
    st.subheader("Estimated LLM Latency")
    lat_rows = sorted(
        [{"skill": r["skill"], "estimated_latency_ms": r.get("estimated_latency_ms", 0)} for r in bm_report],
        key=lambda x: x["estimated_latency_ms"],
        reverse=True,
    )
    st.dataframe(lat_rows[:10], use_container_width=True)

with tabs[4]:
    st.subheader("Per-Skill Detail")
    names = [r["skill"] for r in bm_report]
    selected = st.selectbox("Select skill", names)
    row = next(r for r in bm_report if r["skill"] == selected)
    col1, col2 = st.columns(2)
    col1.metric("Benchmark Score", row["benchmark_score"])
    col1.metric("Rules", row["rule_count"])
    col1.metric("Original Tokens", row["original_prompt_tokens"])
    col2.metric("Best Format", row["ranking"][0].upper() if row.get("ranking") else "—")
    col2.metric("Complexity", row["execution_complexity"])
    col2.metric("Est. Latency ms", row.get("estimated_latency_ms", 0))
    st.subheader("Format Breakdown")
    st.dataframe(row.get("formats", []), use_container_width=True)
