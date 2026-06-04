"""
SecureAI Skills — AI Skill Analysis, Security, and Governance Framework
Standalone Streamlit application entry point.

Run:  streamlit run app.py
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import html
import json
import math
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from agents.ingest import ingest_bytes
from agents.llm import LocalLLMClient, _read_env
from agents.orchestrator import DEFAULT_OUTPUT_DIR, run_all
from agents.agent1 import run_agent1
from agents.agent2 import run_agent2
from agents.agent3 import run_agent3

REPORT_PATH = DEFAULT_OUTPUT_DIR / "full-report.json"
A1_PATH = DEFAULT_OUTPUT_DIR / "agent1" / "agent1-report.json"
A2_PATH = DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json"
A3_PATH = DEFAULT_OUTPUT_DIR / "agent3" / "agent3-report.json"


# ── Async helper ──────────────────────────────────────────────────────────────

def _run_async(coro: Any) -> Any:
    """Run an async coroutine safely from Streamlit's synchronous context.

    Streamlit may already own an event loop; spawning a dedicated thread
    gives asyncio.run() a clean loop with no conflict.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


# ── Data helpers ──────────────────────────────────────────────────────────────

def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _llm_status() -> dict:
    env = _read_env(Path("."))
    client = LocalLLMClient(env)
    connected = bool(client.base_url) and client.enabled
    return {
        "connected": connected,
        "base_url": client.base_url or "",
        "model": client.model,
        "mock_mode": not connected,
        "max_retries": client.max_retries,
        "timeout": client.timeout,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

# set_page_config MUST be the first Streamlit call and called exactly once (here, in app.py)
st.set_page_config(
    page_title="SecureAI Skills Framework",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/nkhader7/secureaiskills",
        "Report a bug": "https://github.com/nkhader7/secureaiskills/issues",
        "About": "SecureAI Skills — AI Skill Analysis, Security, and Governance Framework",
    },
)


def _inject_dark_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg: #080b12;
          --panel: #111827;
          --panel-2: #0f172a;
          --line: #243244;
          --text: #e5edf7;
          --muted: #94a3b8;
          --cyan: #38bdf8;
          --green: #22c55e;
          --amber: #f59e0b;
          --red: #ef4444;
        }
        .stApp {
          background:
            radial-gradient(circle at 18% 8%, rgba(56, 189, 248, 0.14), transparent 30%),
            linear-gradient(180deg, #080b12 0%, #0b1020 42%, #080b12 100%);
          color: var(--text);
        }
        section[data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0b1220 0%, #080b12 100%);
          border-right: 1px solid var(--line);
        }
        div[data-testid="stMetric"] {
          background: rgba(17, 24, 39, 0.82);
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 8px;
          padding: 14px 16px;
          box-shadow: 0 18px 50px rgba(0, 0, 0, 0.24);
        }
        div[data-testid="stMetric"] label,
        .stCaptionContainer,
        p, li {
          color: var(--muted);
        }
        h1, h2, h3 {
          color: #f8fafc;
          letter-spacing: 0;
        }
        .stTabs [data-baseweb="tab-list"] {
          gap: 4px;
          border-bottom: 1px solid var(--line);
        }
        .stTabs [data-baseweb="tab"] {
          background: transparent;
          border-radius: 6px 6px 0 0;
          color: var(--muted);
        }
        .stTabs [aria-selected="true"] {
          color: #f8fafc;
          border-bottom: 2px solid var(--cyan);
        }
        div[data-testid="stDataFrame"] {
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 8px;
          overflow: hidden;
        }
        .stButton button, .stDownloadButton button {
          border-radius: 6px;
          border: 1px solid rgba(56, 189, 248, 0.35);
          background: linear-gradient(180deg, rgba(14, 165, 233, 0.22), rgba(2, 132, 199, 0.14));
          color: #eff6ff;
        }
        .stButton button:hover, .stDownloadButton button:hover {
          border-color: var(--cyan);
          color: #ffffff;
        }
        code {
          color: #bae6fd;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _graph_html(graph: dict[str, Any], title: str) -> str:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    width = 940
    height = 540
    cx = width / 2
    cy = height / 2
    radius = min(width, height) * 0.34
    node_ids = [str(n.get("id", n.get("label", idx))) for idx, n in enumerate(nodes)]
    if not node_ids:
        node_ids = ["empty"]
        nodes = [{"id": "empty", "label": "No nodes"}]
    positions = {}
    for idx, node_id in enumerate(node_ids):
        angle = (2 * math.pi * idx / max(len(node_ids), 1)) - math.pi / 2
        positions[node_id] = {
            "x": cx + radius * math.cos(angle),
            "y": cy + radius * math.sin(angle),
        }

    edge_markup = []
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source not in positions or target not in positions:
            continue
        a = positions[source]
        b = positions[target]
        edge_markup.append(
            f'<line x1="{a["x"]:.1f}" y1="{a["y"]:.1f}" x2="{b["x"]:.1f}" y2="{b["y"]:.1f}" '
            'stroke="rgba(148,163,184,.55)" stroke-width="1.4" marker-end="url(#arrow)" />'
        )

    node_markup = []
    for idx, node in enumerate(nodes):
        node_id = str(node.get("id", idx))
        p = positions.get(node_id, {"x": cx, "y": cy})
        label = html.escape(str(node.get("label", node_id)))
        score = node.get("score")
        covered = node.get("covered")
        color = "#38bdf8"
        if covered is True:
            color = "#22c55e"
        elif covered is False:
            color = "#f59e0b"
        elif isinstance(score, (int, float)):
            color = "#22c55e" if score >= 8 else "#f59e0b" if score >= 5 else "#ef4444"
        node_markup.append(
            f'''
            <g class="node" transform="translate({p["x"]:.1f},{p["y"]:.1f})">
              <circle r="24" fill="{color}" fill-opacity=".18" stroke="{color}" stroke-width="2"></circle>
              <circle r="6" fill="{color}"></circle>
              <text y="43" text-anchor="middle">{label}</text>
            </g>
            '''
        )

    safe_title = html.escape(title.replace("_", " ").title())
    return f"""
    <div class="graph-shell">
      <div class="graph-title">{safe_title}</div>
      <svg viewBox="0 0 {width} {height}" role="img" aria-label="{safe_title}">
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="rgba(148,163,184,.7)" />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="#09111f" stroke="#1f2a3a"/>
        <g opacity=".55">
          <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#1f2a3a" stroke-dasharray="5 9"/>
          <circle cx="{cx}" cy="{cy}" r="{radius * .62}" fill="none" stroke="#172033"/>
        </g>
        <g>{''.join(edge_markup)}</g>
        <g filter="url(#glow)">{''.join(node_markup)}</g>
      </svg>
      <div class="graph-meta">{len(nodes)} nodes · {len(edges)} edges</div>
    </div>
    <style>
      .graph-shell {{
        background: linear-gradient(180deg, #0b1220, #070b12);
        border: 1px solid #243244;
        border-radius: 8px;
        padding: 14px;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: #e5edf7;
      }}
      .graph-title {{
        font-size: 16px;
        font-weight: 700;
        margin: 0 0 10px 2px;
      }}
      .graph-meta {{
        color: #94a3b8;
        font-size: 12px;
        margin-top: 8px;
      }}
      svg text {{
        fill: #dbeafe;
        font-size: 12px;
        font-weight: 600;
      }}
      .node:hover circle:first-child {{
        fill-opacity: .34;
      }}
    </style>
    """


def main() -> None:
    st.title("🔒 SecureAI Skills Framework")
    st.caption(
        "Ingest any AI skill → analyze structure, security, compliance, "
        "coverage, testing, benchmarking → generate actionable reports."
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # LLM status
        llm = _llm_status()
        if llm["connected"]:
            st.success(f"🟢 LLM connected\n`{llm['base_url']}`\nModel: `{llm['model']}`")
        else:
            st.warning(
                "🟡 LLM not configured — running in **deterministic offline mode**.\n\n"
                "Set `LLM_BASE_URL` and `LLM_MODEL` in `.env` to enable real LLM analysis."
            )
        with st.expander("Configure LLM"):
            st.code(
                "# .env\nLLM_BASE_URL=http://localhost:11434/v1\n"
                "LLM_MODEL=llama3\nLLM_TIMEOUT=60\nLLM_MAX_RETRIES=3",
                language="bash",
            )
        st.divider()

        # Run controls
        st.header("Run Analysis")
        skill_input = st.text_area(
            "Skills (one per line, blank = all 26)",
            height=100,
            help="Leave blank to analyze all skills in the skills/ directory.",
        )
        skills = [s.strip() for s in skill_input.splitlines() if s.strip()]

        if st.button("▶ Run All Modules", type="primary", use_container_width=True):
            with st.spinner("Running all analysis modules in parallel…"):
                try:
                    _run_async(run_all(skills=skills or None))
                    st.success("Analysis complete. Reload pages to see results.")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Module 1", use_container_width=True, help="Skill Intelligence"):
                with st.spinner("Running…"):
                    _run_async(run_agent1(skills=skills or None))
                st.success("Done.")
        with col2:
            if st.button("Module 2", use_container_width=True, help="Security & Compliance"):
                with st.spinner("Running…"):
                    _run_async(run_agent2(skills=skills or None))
                st.success("Done.")
        with col3:
            if st.button("Module 3", use_container_width=True, help="Test & Benchmark"):
                with st.spinner("Running…"):
                    _run_async(run_agent3(skills=skills or None))
                st.success("Done.")

        st.divider()
        st.header("Upload Skill")
        uploaded = st.file_uploader(
            "Single file, ZIP, or collection",
            type=["md", "yaml", "yml", "toml", "json", "py", "txt", "zip"],
            help="Uploads are safely extracted to a temporary workspace before analysis.",
        )
        if uploaded and st.button("Analyze Upload", use_container_width=True):
            try:
                ingested = ingest_bytes(uploaded.name, uploaded.getvalue())
                with st.spinner(f"Analyzing {len(ingested.files)} file(s)…"):
                    _run_async(
                        run_all(
                            skills_dir=str(ingested.skills_dir),
                            output_dir=str(DEFAULT_OUTPUT_DIR),
                        )
                    )
                for warning in ingested.warnings:
                    st.warning(warning)
                st.success(f"Upload `{ingested.upload_id}` analyzed.")
            except ValueError as exc:
                st.error(str(exc))

        st.divider()
        st.caption("Navigate to detailed pages using the sidebar navigation above.")

    # ── Dashboard ─────────────────────────────────────────────────────────────
    full = _load(REPORT_PATH)
    a1 = _load(A1_PATH)
    a2 = _load(A2_PATH)
    a3 = _load(A3_PATH)

    if not full and not a1 and not a2 and not a3:
        st.info(
            "No analysis reports found yet.  \n"
            "Click **▶ Run All Modules** in the sidebar or navigate to **1 Upload** "
            "to upload a skill file."
        )
        _show_getting_started()
        return

    # Score banner
    if full:
        decision = str(full.get("pass_fail_decision", "—")).upper()
        risk = str(full.get("overall_risk", "—")).upper()
        badge = "🟢" if decision == "PASS" else "🔴"
        st.subheader(f"{badge} {decision}  ·  Risk: {risk}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        for col, key, label in [
            (c1, "overall_score", "Overall"),
            (c2, "security_score", "Security"),
            (c3, "compliance_score", "Compliance"),
            (c4, "validation_score", "Validation"),
            (c5, "coverage_score", "Coverage"),
            (c6, "benchmark_score", "Benchmark"),
        ]:
            col.metric(label, full.get(key, "—"))
        st.divider()

    # Inline tabs (summary view — full detail is in the sidebar pages)
    tabs = st.tabs([
        "Structure", "Security", "Compliance",
        "Coverage", "Tests", "Benchmarks",
        "Visualizations", "Final Report", "Raw JSON",
    ])

    with tabs[0]:
        st.subheader("Skill Structure")
        if a1.get("coverage_report"):
            st.dataframe(a1["coverage_report"], use_container_width=True)
        if a1.get("skill_results"):
            names = [r["skill"] for r in a1["skill_results"] if "skill" in r]
            sel = st.selectbox("Inspect skill", names, key="tab_struct_skill")
            row = next((r for r in a1["skill_results"] if r.get("skill") == sel), {})
            col1, col2 = st.columns(2)
            with col1:
                st.json(row.get("discovery", {}))
            with col2:
                st.json(row.get("validation", {}))

    with tabs[1]:
        st.subheader("Security Analysis")
        rs = a2.get("risk_summary", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("High Risk", rs.get("high", 0))
        c2.metric("Medium Risk", rs.get("medium", 0))
        c3.metric("Low Risk", rs.get("low", 0))
        st.dataframe(a2.get("security_report", []), use_container_width=True)
        for f in a2.get("all_findings", [])[:20]:
            st.write(f"- {f}")

    with tabs[2]:
        st.subheader("Compliance Analysis")
        st.dataframe(a2.get("compliance_report", []), use_container_width=True)

    with tabs[3]:
        st.subheader("Security Testing Coverage")
        cmap = a1.get("coverage_map", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Coverage Score", f"{round(float(cmap.get('coverage_score', 0)) * 100, 1)}%")
        c2.metric("Covered Domains", len(cmap.get("covered_domains", [])))
        c3.metric("Missing Domains", len(cmap.get("missing_domains", [])))
        col1, col2 = st.columns(2)
        with col1:
            for d in cmap.get("covered_domains", []):
                st.write(f"✓ {d}")
        with col2:
            for d in cmap.get("missing_domains", []):
                st.write(f"✗ {d}")

    with tabs[4]:
        st.subheader("Test Generation")
        st.dataframe(a3.get("coverage_report", []), use_container_width=True)
        fails = [r for r in a3.get("ci_cd_report", []) if r.get("decision") == "fail"]
        if fails:
            st.error(f"{len(fails)} skill(s) failed CI gate.")
        else:
            st.success("All skills pass CI gate.")
        st.dataframe(a3.get("ci_cd_report", []), use_container_width=True)

    with tabs[5]:
        st.subheader("Benchmarking")
        bm_rows = []
        for skill in a3.get("benchmark_report", []):
            best = skill["formats"][0] if skill.get("formats") else {}
            bm_rows.append({
                "skill": skill["skill"],
                "best_format": best.get("format", "—").upper(),
                "score": skill["benchmark_score"],
                "complexity": skill["execution_complexity"],
            })
        st.dataframe(bm_rows, use_container_width=True)

    with tabs[6]:
        st.subheader("Execution Graphs")
        graph_artifacts = a3.get("graph_artifacts", {})
        if graph_artifacts:
            skill_names = sorted(graph_artifacts.keys())
            sel = st.selectbox("Select skill", skill_names, key="graph_skill")
            graphs = graph_artifacts[sel]
            graph_tabs = st.tabs(list(graphs.keys()))
            for gt, (gname, gdata) in zip(graph_tabs, graphs.items()):
                with gt:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Nodes")
                        st.dataframe(gdata.get("nodes", []), use_container_width=True)
                    with col2:
                        st.caption("Edges")
                        st.dataframe(gdata.get("edges", []), use_container_width=True)
        else:
            st.info("Run Module 3 to generate graph artifacts.")

    with tabs[7]:
        st.subheader("Final Report")
        if full:
            summary = full.get("summary", {})
            if summary:
                st.json(summary)
            st.subheader("Recommendations")
            for rec in full.get("recommendations", []):
                st.write(f"- {rec}")
            st.download_button(
                "⬇ Download Full Report JSON",
                json.dumps(full, indent=2),
                file_name="secureai-full-report.json",
                mime="application/json",
            )
        else:
            st.info("Run all modules to generate the combined report.")

    with tabs[8]:
        active = full or a1 or a2 or a3
        if active:
            label = "full-report.json" if full else "partial-report.json"
            st.download_button(f"⬇ Download {label}", json.dumps(active, indent=2), label)
            st.json(active)


def _show_getting_started() -> None:
    st.markdown("---")
    st.subheader("Getting Started")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Configure LLM** *(optional)*")
        st.code("cp .env.example .env\n# Edit LLM_BASE_URL and LLM_MODEL", language="bash")
    with col2:
        st.markdown("**2. Run analysis**")
        st.code("# Click ▶ Run All Modules\n# or run via CLI:\npython ci.py", language="bash")
    with col3:
        st.markdown("**3. Upload a custom skill**")
        st.code("# Use the Upload Skill\n# section in the sidebar\n# or navigate to page 1", language="bash")


if __name__ == "__main__":
    main()
