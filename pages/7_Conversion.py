"""Page 7 — Skill Conversion: view and download converted skill formats."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A3_PATH = Path("output/agent3/agent3-report.json")
CONVERTED_DIR = Path("output/agent3/converted")
st.title("Skill Conversion — Agent 3")
st.caption("Converted formats: Markdown · YAML · TOML · JSON · Python. Intent, logic, and security constraints preserved.")

a3: dict = {}
if A3_PATH.exists():
    a3 = json.loads(A3_PATH.read_text(encoding="utf-8"))

if not a3:
    st.info("No Agent 3 report found. Run the analysis from the home page.")
    st.stop()

skill_results = a3.get("skill_results", [])
if not skill_results:
    st.info("No skill results available.")
    st.stop()

names = [r["skill"] for r in skill_results]
selected = st.selectbox("Select skill to inspect", names)
row = next(r for r in skill_results if r["skill"] == selected)
conversions = row.get("conversions", {})

FORMATS = ["markdown", "yaml", "toml", "json", "python"]
fmt_tabs = st.tabs([f.upper() for f in FORMATS] + ["Size Comparison"])

for i, fmt in enumerate(FORMATS):
    with fmt_tabs[i]:
        item = conversions.get(fmt, {})
        if not item:
            st.info("No conversion available.")
            continue
        col1, col2, col3 = st.columns(3)
        col1.metric("Bytes", item.get("bytes", 0))
        col2.metric("Est. Tokens", item.get("tokens_estimate", 0))
        col3.metric("Preserved fields", len(item.get("preserves", [])))
        content = item.get("content", "")
        st.code(content[:3000] + ("\n…" if len(content) > 3000 else ""), language=fmt if fmt != "markdown" else "markdown")
        ext = "md" if fmt == "markdown" else fmt
        st.download_button(
            f"Download {fmt.upper()}",
            content,
            file_name=f"{selected}.{ext}",
            mime="text/plain",
            key=f"dl_{selected}_{fmt}",
        )

with fmt_tabs[-1]:
    st.subheader("Format Size Comparison")
    rows_data = []
    for fmt in FORMATS:
        item = conversions.get(fmt, {})
        rows_data.append({
            "Format": fmt.upper(),
            "Bytes": item.get("bytes", 0),
            "Tokens": item.get("tokens_estimate", 0),
            "Efficiency Score": next(
                (r["format_efficiency_score"] for r in row.get("benchmark", {}).get("formats", []) if r["format"] == fmt),
                "—",
            ),
        })
    st.dataframe(rows_data, use_container_width=True)
    bm_ranking = row.get("benchmark", {}).get("ranking", [])
    if bm_ranking:
        st.info(f"Best format by efficiency: **{bm_ranking[0].upper()}**")
