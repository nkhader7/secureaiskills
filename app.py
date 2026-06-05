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
from agents.llm import LocalLLMClient, _read_env, safe_load_yaml
from agents.orchestrator import DEFAULT_OUTPUT_DIR, run_all
from agents.agent1 import SKILL_CATEGORY_MAP
from agents.agent2 import SKILL_SECURITY_PROFILES
from pages._shared import sidebar_nav

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


def _available_skills() -> list[str]:
    skills_dir = Path("skills")
    if not skills_dir.exists():
        return []
    return sorted(d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith("_"))


def _skill_description(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.strip().startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    for line in text.splitlines():
        clean = line.strip()
        if clean and not clean.startswith("---") and not clean.startswith("#"):
            return clean[:180]
    return ""


def _skill_catalog() -> list[dict[str, Any]]:
    skills_dir = Path("skills")
    if not skills_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("_")):
        profile = SKILL_SECURITY_PROFILES.get(skill_dir.name, {})
        rules_path = skill_dir / "references" / "rules.yaml"
        rules_data = safe_load_yaml(rules_path)
        rules = rules_data.get("rules", []) if isinstance(rules_data, dict) else []
        rows.append({
            "skill": skill_dir.name,
            "category": SKILL_CATEGORY_MAP.get(skill_dir.name, profile.get("domain", "General Security")),
            "subcategory": profile.get("subcategory", "Security Scanning"),
            "rules": len(rules),
            "standards": ", ".join((profile.get("owasp_top10") or [])[:4]) or "-",
            "description": _skill_description(skill_dir),
        })
    return rows


def _render_skill_catalog(catalog: list[dict[str, Any]], latest_count: int) -> None:
    st.subheader("Skill Catalog")
    if not catalog:
        st.info("No local skills found in `skills/`.")
        return
    categories = sorted({row["category"] for row in catalog})
    c1, c2, c3 = st.columns(3)
    c1.metric("Local Skills", len(catalog))
    c2.metric("Categories", len(categories))
    c3.metric("In Latest Report", latest_count)

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_category = st.selectbox("Category", ["All"] + categories, key="catalog_category")
    filtered = catalog if selected_category == "All" else [r for r in catalog if r["category"] == selected_category]
    with col2:
        selected_catalog_skill = st.selectbox(
            "Skill",
            [r["skill"] for r in filtered],
            key="catalog_skill",
        )

    st.dataframe(
        filtered,
        column_order=["skill", "category", "subcategory", "rules", "standards", "description"],
        use_container_width=True,
        hide_index=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Validate Catalog Skill", type="primary", use_container_width=True):
            with st.spinner(f"Validating `{selected_catalog_skill}`..."):
                try:
                    _run_async(run_all(skills=[selected_catalog_skill]))
                    st.success(f"`{selected_catalog_skill}` validation complete.")
                except Exception as exc:
                    st.error(f"Validation failed: {exc}")
    with col_b:
        if st.button("Validate Full Collection", use_container_width=True):
            with st.spinner("Validating full local skill collection..."):
                try:
                    _run_async(run_all(skills=None))
                    st.success("Full collection validation complete.")
                except Exception as exc:
                    st.error(f"Validation failed: {exc}")


def _render_validation_flow() -> None:
    st.subheader("Validation Flow")
    steps = [
        ("1", "Ingest", "Upload file, ZIP, collection, or choose local skill"),
        ("2", "Structure", "Intent, references, dependencies, execution flow"),
        ("3", "Security", "Unsafe instructions, secrets, permissions, governance"),
        ("4", "Tests", "Test project, conversions, mock responses, CI output"),
        ("5", "Benchmark", "Token evaluator, format ranking, graphs, reports"),
    ]
    cols = st.columns(len(steps))
    for col, (num, title, body) in zip(cols, steps):
        with col:
            st.metric(f"{num}. {title}", body)


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
    _inject_dark_theme()
    st.title("SecureAI Skill Validation")
    st.caption(
        "Upload a skill for full validation, or choose an existing skill from the repository."
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        sidebar_nav()
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

        st.header("Validate")
        uploaded = st.file_uploader(
            "Upload skill, ZIP, or collection",
            type=["md", "yaml", "yml", "toml", "json", "py", "txt", "zip"],
            help="Uploads are safely extracted to a temporary workspace before validation.",
        )

        selected_skill = None
        if uploaded:
            st.caption("Upload detected. Validation will run against the uploaded workspace.")
        else:
            st.caption("No upload selected. Choose one existing skill or validate the full local collection.")
            skill_names = _available_skills()
            if skill_names:
                selected_skill = st.selectbox("Existing skills", skill_names)
                st.caption(f"{len(skill_names)} local skill(s) available.")
            else:
                st.warning("No local skills found in `skills/`.")

        if uploaded and st.button("Validate Upload", type="primary", use_container_width=True):
            try:
                ingested = ingest_bytes(uploaded.name, uploaded.getvalue())
                with st.spinner(f"Validating {len(ingested.files)} file(s)..."):
                    _run_async(
                        run_all(
                            skills_dir=str(ingested.skills_dir),
                            output_dir=str(DEFAULT_OUTPUT_DIR),
                        )
                    )
                for warning in ingested.warnings:
                    st.warning(warning)
                st.success(f"Upload `{ingested.upload_id}` validation complete.")
            except ValueError as exc:
                st.error(str(exc))
        elif not uploaded and st.button("Validate Selected Skill", type="primary", use_container_width=True):
            if selected_skill:
                with st.spinner(f"Validating `{selected_skill}`..."):
                    try:
                        _run_async(run_all(skills=[selected_skill]))
                        st.success(f"`{selected_skill}` validation complete.")
                    except Exception as exc:
                        st.error(f"Validation failed: {exc}")
        elif not uploaded and st.button("Validate All Local Skills", use_container_width=True):
            with st.spinner("Validating all local skills..."):
                try:
                    _run_async(run_all(skills=None))
                    st.success("All local skills validation complete.")
                except Exception as exc:
                    st.error(f"Validation failed: {exc}")

        st.divider()
        st.caption("Results refresh after validation completes.")

    # ── Dashboard ─────────────────────────────────────────────────────────────
    full = _load(REPORT_PATH)
    a1 = _load(A1_PATH)
    a2 = _load(A2_PATH)
    a3 = _load(A3_PATH)
    catalog = _skill_catalog()
    latest_count = len(a3.get("skill_results", [])) if a3 else 0
    _render_validation_flow()
    st.divider()
    _render_skill_catalog(catalog, latest_count)
    st.divider()

    if not full and not a1 and not a2 and not a3:
        st.info(
            "No analysis reports found yet.  \n"
            "Upload a skill or choose an existing skill, then run validation."
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
        "Token Size", "Visualizations", "Final Report", "Raw JSON",
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
            token_eval = skill.get("token_evaluator", {})
            bm_rows.append({
                "skill": skill["skill"],
                "best_token_format": str(token_eval.get("best_token_format", "-")).upper(),
                "lowest_context_tokens": token_eval.get("lowest_context_tokens", 0),
                "highest_context_tokens": token_eval.get("highest_context_tokens", 0),
                "best_format": best.get("format", "—").upper(),
                "score": skill["benchmark_score"],
                "complexity": skill["execution_complexity"],
            })
        st.dataframe(bm_rows, use_container_width=True)
        reports = a3.get("benchmark_report", [])
        if reports:
            selected_benchmark = st.selectbox("Select benchmark", [r["skill"] for r in reports], key="benchmark_skill")
            selected = next((r for r in reports if r["skill"] == selected_benchmark), None)
            if selected:
                st.caption("Token evaluator")
                st.json(selected.get("token_evaluator", {}))
                st.caption("Format token metrics")
                st.dataframe(selected.get("formats", []), use_container_width=True)

    with tabs[6]:
        st.subheader("Token Size by Validation Step")
        token_summary = full.get("token_summary", {}) if full else {}
        token_rows = full.get("token_report", []) if full else []
        c1, c2, c3 = st.columns(3)
        c1.metric("Prompt Tokens", token_summary.get("total_prompt_tokens", 0))
        c2.metric("Completion Tokens", token_summary.get("total_completion_tokens", 0))
        c3.metric("Context Tokens", token_summary.get("total_context_tokens", 0))
        if token_summary.get("largest_step"):
            st.caption("Largest token step")
            st.json(token_summary["largest_step"])
        if token_rows:
            st.dataframe(token_rows, use_container_width=True)
        else:
            st.info("Run validation to calculate token sizes for each step.")

    with tabs[7]:
        st.subheader("Execution Graphs")
        graph_artifacts = a3.get("graph_artifacts", {})
        if graph_artifacts:
            skill_names = sorted(graph_artifacts.keys())
            sel = st.selectbox("Select skill", skill_names, key="graph_skill")
            graphs = graph_artifacts[sel]
            graph_tabs = st.tabs(list(graphs.keys()))
            for gt, (gname, gdata) in zip(graph_tabs, graphs.items()):
                with gt:
                    components.html(_graph_html(gdata, gname), height=650, scrolling=False)
                    with st.expander("Graph data"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption("Nodes")
                            st.dataframe(gdata.get("nodes", []), use_container_width=True)
                        with col2:
                            st.caption("Edges")
                            st.dataframe(gdata.get("edges", []), use_container_width=True)
        else:
            st.info("Run validation to generate graph artifacts.")

    with tabs[8]:
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
            st.info("Run validation to generate the combined report.")

    with tabs[9]:
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
        st.code("# Click Validate Selected Skill\n# or run via CLI:\npython ci.py", language="bash")
    with col3:
        st.markdown("**3. Upload a custom skill**")
        st.code("# Use the upload control\n# in the sidebar", language="bash")


if __name__ == "__main__":
    main()
