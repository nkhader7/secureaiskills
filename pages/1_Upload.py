"""Page 1 — Upload Skill: ingest a skill file, ZIP, or repository."""
from __future__ import annotations

import asyncio
import concurrent.futures
import json
from pathlib import Path

import streamlit as st

from agents.ingest import ingest_bytes, ingest_path
from agents.orchestrator import DEFAULT_OUTPUT_DIR, run_all

st.title("Upload Skill")
st.caption("Ingest a single skill file, ZIP archive, skill collection, or repository for full analysis.")


def _run(skills_dir: str) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(
            asyncio.run,
            run_all(skills_dir=skills_dir, output_dir=str(DEFAULT_OUTPUT_DIR)),
        ).result()


tab_upload, tab_path = st.tabs(["Upload File", "Local Path"])

with tab_upload:
    st.subheader("Upload a skill file or ZIP archive")
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Supported formats: .md .yaml .yml .json .toml .py .zip",
            type=["md", "yaml", "yml", "toml", "json", "py", "txt", "zip"],
        )
    with col2:
        st.markdown("**Supported inputs**")
        st.markdown("""
- Single skill file (any format)
- ZIP archive of skill collection
- Multi-file repository bundles
- SKILL.md + references/ folder
        """)

    if uploaded:
        st.info(f"File: `{uploaded.name}` — {len(uploaded.getvalue()) // 1024} KB")
        if st.button("Analyze Upload", type="primary"):
            try:
                data = uploaded.getvalue()
                with st.spinner("Ingesting upload…"):
                    ingested = ingest_bytes(uploaded.name, data)
                for w in ingested.warnings:
                    st.warning(w)
                st.success(f"Workspace ready — upload ID: `{ingested.upload_id}`")
                st.write(f"Skills directory: `{ingested.skills_dir}`")
                st.write(f"Files extracted: {len(ingested.files)}")
                with st.expander("File list"):
                    for f in ingested.files[:60]:
                        st.text(f)

                with st.spinner("Running all 3 agents in parallel…"):
                    report = _run(str(ingested.skills_dir))
                st.session_state["report"] = report
                st.session_state["upload_id"] = ingested.upload_id
                decision = report.get("pass_fail_decision", "?").upper()
                risk = report.get("overall_risk", "?").upper()
                score = report.get("overall_score", "?")
                st.metric("Decision", decision)
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Overall Risk", risk)
                col_b.metric("Overall Score", score)
                col_c.metric("Skills Analyzed", report.get("skills_analyzed", 0))
                st.download_button(
                    "Download Full Report JSON",
                    json.dumps(report, indent=2),
                    file_name="secureai-full-report.json",
                    mime="application/json",
                )
            except ValueError as exc:
                st.error(str(exc))

with tab_path:
    st.subheader("Analyze a local path")
    path_input = st.text_input("Absolute path to skill directory, file, or ZIP")
    if path_input and st.button("Analyze Path", type="primary"):
        path = Path(path_input)
        try:
            with st.spinner("Ingesting path…"):
                ingested = ingest_path(path)
            for w in ingested.warnings:
                st.warning(w)
            st.success(f"Workspace ready — upload ID: `{ingested.upload_id}`")
            with st.spinner("Running all 3 agents…"):
                report = _run(str(ingested.skills_dir))
            st.session_state["report"] = report
            decision = report.get("pass_fail_decision", "?").upper()
            st.metric("Decision", decision)
            st.download_button(
                "Download Full Report JSON",
                json.dumps(report, indent=2),
                file_name="secureai-full-report.json",
                mime="application/json",
            )
        except (ValueError, FileNotFoundError) as exc:
            st.error(str(exc))
