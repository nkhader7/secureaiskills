"""Page 1 — Upload Skill"""
from __future__ import annotations

import asyncio
import concurrent.futures
import json
from pathlib import Path

import streamlit as st

from agents.ingest import ingest_bytes, ingest_path
from agents.orchestrator import DEFAULT_OUTPUT_DIR, run_all
from pages._shared import inject_theme, sidebar_nav, badge, divider, empty_state, panel

inject_theme()
sidebar_nav()

st.title("Upload Skill")
st.caption("Ingest any skill format and run the full analysis pipeline.")

FILE_ICONS = {".md": "📝", ".yaml": "📋", ".yml": "📋", ".json": "📦",
              ".toml": "⚙️", ".py": "🐍", ".zip": "🗜️", ".txt": "📄"}


def _run(skills_dir: str) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(
            asyncio.run,
            run_all(skills_dir=skills_dir, output_dir=str(DEFAULT_OUTPUT_DIR)),
        ).result()


tab_upload, tab_path, tab_guide = st.tabs(["📁  Upload File", "📂  Local Path", "📖  Guide"])

with tab_upload:
    col1, col2 = st.columns([3, 1], gap="large")
    with col1:
        uploaded = st.file_uploader(
            "Drop a skill file, ZIP archive, or skill collection",
            type=["md", "yaml", "yml", "toml", "json", "py", "txt", "zip"],
            label_visibility="collapsed",
        )
    with col2:
        st.markdown(
            panel("Supported", "<br>".join(
                f'<div style="color:#94a3b8;font-size:12px;padding:2px 0">{i}&nbsp;{n}</div>'
                for n, i in [("Single skill file", "📝"), ("ZIP archive", "🗜️"),
                              ("SKILL.md + references/", "📁"), ("Repository bundle", "🗂️")]
            )),
            unsafe_allow_html=True,
        )

    if uploaded:
        ext = Path(uploaded.name).suffix.lower()
        icon = FILE_ICONS.get(ext, "📄")
        size_kb = len(uploaded.getvalue()) // 1024
        st.markdown(
            f'<div style="background:rgba(14,21,37,.8);border:1px solid rgba(56,189,248,.25);'
            f'border-radius:8px;padding:12px 16px;display:flex;align-items:center;gap:12px;margin:8px 0">'
            f'<span style="font-size:28px">{icon}</span>'
            f'<div><div style="color:#f1f5fb;font-weight:600">{uploaded.name}</div>'
            f'<div style="color:#7a90b0;font-size:12px">{size_kb} KB · {ext.upper()}</div></div></div>',
            unsafe_allow_html=True,
        )

        if st.button("▶  Analyze", type="primary", use_container_width=True):
            try:
                with st.spinner("Ingesting upload…"):
                    ingested = ingest_bytes(uploaded.name, uploaded.getvalue())
                for w in ingested.warnings:
                    st.warning(w)

                st.markdown(
                    f'<div style="color:#22c55e;font-size:13px;margin:8px 0">'
                    f'✓ Workspace ready — <code>{ingested.upload_id}</code> · '
                    f'{len(ingested.files)} file(s) extracted</div>',
                    unsafe_allow_html=True,
                )
                with st.expander(f"File list ({len(ingested.files)})"):
                    for f in ingested.files[:60]:
                        st.text(f)

                progress = st.progress(0, text="Running analysis pipeline…")
                with st.spinner("Running all validation modules in parallel…"):
                    report = _run(str(ingested.skills_dir))
                progress.progress(100, text="Analysis complete")

                st.session_state["report"] = report
                decision = report.get("pass_fail_decision", "?")
                risk = report.get("overall_risk", "?")
                score = report.get("overall_score", 0)

                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Decision", decision.upper())
                col_b.metric("Risk", risk.upper())
                col_c.metric("Score", score)
                col_d.metric("Skills", report.get("skills_analyzed", 0))

                st.download_button(
                    "⬇  Download Full Report",
                    json.dumps(report, indent=2),
                    file_name="secureai-report.json",
                    mime="application/json",
                    use_container_width=True,
                )
            except ValueError as exc:
                st.error(str(exc))

with tab_path:
    path_input = st.text_input(
        "Absolute path to skill directory, file, or ZIP archive",
        placeholder="/path/to/skills/  or  /path/to/skill.yaml",
    )
    if path_input and st.button("▶  Analyze Path", type="primary"):
        path = Path(path_input)
        try:
            with st.spinner("Ingesting…"):
                ingested = ingest_path(path)
            for w in ingested.warnings:
                st.warning(w)
            with st.spinner("Running analysis…"):
                report = _run(str(ingested.skills_dir))
            st.session_state["report"] = report
            decision = report.get("pass_fail_decision", "?")
            col_a, col_b = st.columns(2)
            col_a.metric("Decision", decision.upper())
            col_b.metric("Skills", report.get("skills_analyzed", 0))
            st.download_button(
                "⬇  Download Report", json.dumps(report, indent=2),
                file_name="secureai-report.json", mime="application/json",
            )
        except (ValueError, FileNotFoundError) as exc:
            st.error(str(exc))

with tab_guide:
    st.markdown(
        panel("How it works",
              '<ol style="color:#94a3b8;font-size:13px;line-height:2;padding-left:18px">'
              "<li>Upload a skill file, ZIP, or point at a local path</li>"
              "<li>The framework extracts and ingests the skill workspace</li>"
              "<li><b style='color:#e2eaf6'>Structure</b> - intent, references, dependencies, functional analysis</li>"
              "<li><b style='color:#e2eaf6'>Security & Compliance</b> - OWASP, CWE, NIST, supply-chain, governance</li>"
              "<li><b style='color:#e2eaf6'>Operational Readiness</b> - tests, conversion, benchmarks, tokens, graphs</li>"
              "<li>Results appear on each page in the sidebar</li>"
              "</ol>",
              ) +
        panel("Supported formats",
              '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;color:#94a3b8">'
              + "".join(
                  f'<div>{icon}&nbsp;<code>{ext}</code>&nbsp;{name}</div>'
                  for ext, icon, name in [
                      (".md", "📝", "SKILL.md with frontmatter"),
                      (".yaml/.yml", "📋", "YAML skill definition"),
                      (".json", "📦", "JSON skill definition"),
                      (".toml", "⚙️", "TOML skill definition"),
                      (".py", "🐍", "Python SKILL = {...}"),
                      (".zip", "🗜️", "Full skill collection"),
                  ]
              )
              + "</div>"),
        unsafe_allow_html=True,
    )
