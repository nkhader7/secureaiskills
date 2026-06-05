"""
Shared theme, CSS injection, and UI components for all SecureAI Skills pages.
Import and call inject_theme() as the first statement in every page.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import streamlit as st

OUTPUT_ROOT = Path("output")

# ── CSS theme ──────────────────────────────────────────────────────────────────

_CSS = """
<style>
/* ── base ── */
:root {
  --bg:      #070a10;
  --panel:   #0e1525;
  --panel2:  #0b1120;
  --line:    #1e2d44;
  --text:    #e2eaf6;
  --muted:   #7a90b0;
  --cyan:    #38bdf8;
  --green:   #22c55e;
  --amber:   #f59e0b;
  --red:     #ef4444;
  --crit:    #dc2626;
}
.stApp {
  background:
    radial-gradient(ellipse at 12% 6%,  rgba(56,189,248,.12), transparent 36%),
    radial-gradient(ellipse at 85% 88%, rgba(56,189,248,.07), transparent 40%),
    linear-gradient(180deg, #070a10 0%, #090e1a 100%);
  color: var(--text);
}
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1120 0%, #07090f 100%);
  border-right: 1px solid var(--line);
}
/* ── headings ── */
h1, h2, h3, h4 { color: #f1f5fb !important; letter-spacing: -0.01em; }
h1 { border-bottom: 1px solid var(--line); padding-bottom: .4rem; margin-bottom: 1.2rem; }
/* ── metrics ── */
div[data-testid="stMetric"] {
  background: rgba(14,21,37,.85) !important;
  border: 1px solid rgba(56,189,248,.18) !important;
  border-radius: 10px !important;
  padding: 16px 18px !important;
  box-shadow: 0 4px 24px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04) !important;
  backdrop-filter: blur(8px);
}
div[data-testid="stMetric"] label { color: var(--muted) !important; font-size:11px !important; letter-spacing:.06em; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--cyan) !important; font-size:1.8rem !important; font-weight:700; }
/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 2px;
  background: rgba(14,21,37,.6);
  border-radius: 8px 8px 0 0;
  padding: 4px 4px 0;
  border-bottom: 1px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  border-radius: 6px 6px 0 0;
  color: var(--muted);
  font-size: 13px;
  padding: 8px 16px;
  border: none;
}
.stTabs [aria-selected="true"] {
  background: rgba(56,189,248,.10) !important;
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}
/* ── dataframes ── */
div[data-testid="stDataFrame"] {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.3);
}
/* ── buttons ── */
.stButton button, .stDownloadButton button {
  border-radius: 6px !important;
  border: 1px solid rgba(56,189,248,.4) !important;
  background: linear-gradient(135deg, rgba(14,165,233,.25), rgba(2,132,199,.14)) !important;
  color: #e0f2fe !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  transition: all .15s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
  border-color: var(--cyan) !important;
  background: linear-gradient(135deg, rgba(14,165,233,.4), rgba(2,132,199,.25)) !important;
  color: #fff !important;
  box-shadow: 0 0 12px rgba(56,189,248,.25);
}
/* ── inputs ── */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  color: var(--text) !important;
  border-radius: 6px !important;
}
/* ── expanders ── */
details summary {
  background: var(--panel2) !important;
  border: 1px solid var(--line) !important;
  border-radius: 6px !important;
  color: var(--muted) !important;
  padding: 8px 14px !important;
}
/* ── info / warning / success banners ── */
div[data-baseweb="notification"] {
  border-radius: 8px !important;
  border-left-width: 3px !important;
}
/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--line); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }
/* ── code ── */
code { color: #7dd3fc !important; background: rgba(56,189,248,.08) !important; }
/* ── caption ── */
.stCaptionContainer p { color: var(--muted) !important; font-size: 12px; }
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def sidebar_nav() -> None:
    """Render the product navigation grouped by user workflow."""
    st.sidebar.markdown("### SecureAI")
    st.sidebar.page_link("app.py", label="Dashboard")
    st.sidebar.page_link("pages/1_Upload.py", label="Upload Skill")

    st.sidebar.markdown("#### Analyze")
    st.sidebar.page_link("pages/2_Structure.py", label="Structure & Function")
    st.sidebar.page_link("pages/3_Security.py", label="Security Review")
    st.sidebar.page_link("pages/4_Compliance.py", label="Compliance Standards")
    st.sidebar.page_link("pages/5_Coverage.py", label="Coverage Map")

    st.sidebar.markdown("#### Operationalize")
    st.sidebar.page_link("pages/6_Testing.py", label="Test Project")
    st.sidebar.page_link("pages/7_Conversion.py", label="Format Conversion")
    st.sidebar.page_link("pages/8_Benchmark.py", label="Benchmark & Tokens")

    st.sidebar.markdown("#### Reports")
    st.sidebar.page_link("pages/9_Report.py", label="Executive Report")
    st.sidebar.divider()


# ── Report loader ──────────────────────────────────────────────────────────────

def load_report(agent: str) -> dict:
    paths = {
        "full":   OUTPUT_ROOT / "full-report.json",
        "agent1": OUTPUT_ROOT / "agent1" / "agent1-report.json",
        "agent2": OUTPUT_ROOT / "agent2" / "agent2-report.json",
        "agent3": OUTPUT_ROOT / "agent3" / "agent3-report.json",
    }
    p = paths.get(agent, OUTPUT_ROOT / "full-report.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── HTML components ────────────────────────────────────────────────────────────

def _risk_color(risk: str) -> str:
    return {"critical": "#dc2626", "high": "#ef4444", "medium": "#f59e0b",
            "low": "#22c55e", "pass": "#22c55e", "fail": "#ef4444"}.get(str(risk).lower(), "#7a90b0")


def badge(text: str, color: str = "#7a90b0") -> str:
    bg = color.replace("#", "")
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;'
        f'font-size:11px;font-weight:700;letter-spacing:.8px;'
        f'border:1px solid {color};background:rgba({_hex_to_rgb(bg)},.15);color:{color}">'
        f'{text.upper()}</span>'
    )


def _hex_to_rgb(h: str) -> str:
    h = h.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"
    return "148,163,184"


def risk_badge(risk: str) -> str:
    return badge(str(risk), _risk_color(str(risk).lower()))


def decision_badge(decision: str) -> str:
    c = "#22c55e" if str(decision).lower() == "pass" else "#ef4444"
    return badge(decision, c)


def score_ring(value: float, label: str, size: int = 88) -> str:
    pct = max(0.0, min(100.0, float(value or 0)))
    r = size * 0.36
    circ = 2 * math.pi * r
    offset = circ * (1 - pct / 100)
    c = "#22c55e" if pct >= 75 else "#f59e0b" if pct >= 50 else "#ef4444"
    cx = size // 2
    return (
        f'<div style="display:inline-flex;flex-direction:column;align-items:center;gap:4px;padding:4px">'
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle cx="{cx}" cy="{cx}" r="{r:.1f}" fill="none" stroke="#1e2d44" stroke-width="7"/>'
        f'<circle cx="{cx}" cy="{cx}" r="{r:.1f}" fill="none" stroke="{c}" stroke-width="7"'
        f' stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"'
        f' stroke-linecap="round" transform="rotate(-90 {cx} {cx})"/>'
        f'<text x="50%" y="50%" text-anchor="middle" dominant-baseline="central"'
        f' fill="#f1f5fb" font-size="{max(10, size//5)}" font-weight="800" font-family="monospace">'
        f'{pct:.0f}</text></svg>'
        f'<span style="color:#7a90b0;font-size:10px;letter-spacing:.8px;font-weight:600">'
        f'{label.upper()}</span></div>'
    )


def score_row(*items: tuple[float, str]) -> None:
    """Render a horizontal row of score rings."""
    html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0">'
    for val, label in items:
        html += score_ring(val, label)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def skill_card(row: dict) -> str:
    name = row.get("skill", "?")
    score = float(row.get("security_effectiveness_score", 0))
    risk = str(row.get("overall_risk", "low")).lower()
    owasp = float(row.get("owasp_coverage_pct", 0))
    cwe = float(row.get("cwe_coverage_pct", 0))
    quality = float(row.get("rule_quality_score", 0))
    gaps = int(row.get("gaps_count", 0))
    rc = _risk_color(risk)
    sc = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    return (
        f'<div style="background:rgba(14,21,37,.75);border:1px solid rgba(30,45,68,.9);'
        f'border-left:3px solid {rc};border-radius:8px;padding:12px 16px;margin:3px 0;'
        f'display:flex;justify-content:space-between;align-items:center;'
        f'transition:border-color .15s">'
        f'<div style="flex:1;min-width:0">'
        f'<div style="color:#f1f5fb;font-weight:600;font-size:13px;font-family:monospace;'
        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</div>'
        f'<div style="color:#7a90b0;font-size:11px;margin-top:3px">'
        f'OWASP&nbsp;<b style="color:#e2eaf6">{owasp:.0f}%</b>&ensp;'
        f'CWE&nbsp;<b style="color:#e2eaf6">{cwe:.0f}%</b>&ensp;'
        f'Quality&nbsp;<b style="color:#e2eaf6">{quality:.0f}%</b>&ensp;'
        f'Gaps&nbsp;<b style="color:{rc}">{gaps}</b></div></div>'
        f'<div style="text-align:right;padding-left:16px;flex-shrink:0">'
        f'<div style="color:{sc};font-size:24px;font-weight:800;font-family:monospace;line-height:1">'
        f'{score:.0f}</div>'
        f'<div style="color:#7a90b0;font-size:9px;letter-spacing:1.2px;font-weight:600">SCORE</div>'
        f'</div></div>'
    )


def panel(title: str, body_html: str, accent: str = "#38bdf8") -> str:
    return (
        f'<div style="background:rgba(14,21,37,.8);border:1px solid rgba(30,45,68,.9);'
        f'border-top:2px solid {accent};border-radius:8px;padding:16px 18px;margin:8px 0">'
        f'<div style="color:#7a90b0;font-size:10px;letter-spacing:1.2px;font-weight:700;margin-bottom:8px">'
        f'{title.upper()}</div>{body_html}</div>'
    )


def divider() -> None:
    st.markdown('<hr style="border:none;border-top:1px solid #1e2d44;margin:16px 0"/>', unsafe_allow_html=True)


def empty_state(message: str, icon: str = "🔍") -> None:
    st.markdown(
        f'<div style="text-align:center;padding:48px 24px;color:#7a90b0">'
        f'<div style="font-size:40px;margin-bottom:12px">{icon}</div>'
        f'<div style="font-size:15px">{message}</div>'
        f'<div style="font-size:12px;margin-top:8px">Run the analysis from the home page.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def finding_item(text: str, severity: str = "medium") -> str:
    c = _risk_color(severity)
    dot = f'<span style="color:{c};font-size:8px;margin-right:8px">●</span>'
    return (
        f'<div style="padding:6px 10px;border-left:2px solid {c};'
        f'background:rgba({_hex_to_rgb(c.lstrip("#"))},.06);'
        f'border-radius:0 4px 4px 0;margin:3px 0;font-size:12px;color:#c8d8ec">'
        f'{dot}{text}</div>'
    )


def progress_bar(pct: float, label: str, color: str = "#38bdf8") -> str:
    pct = max(0.0, min(100.0, float(pct)))
    return (
        f'<div style="margin:4px 0">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
        f'<span style="font-size:11px;color:#7a90b0">{label}</span>'
        f'<span style="font-size:11px;color:#e2eaf6;font-weight:600">{pct:.0f}%</span></div>'
        f'<div style="background:#1e2d44;border-radius:4px;height:5px">'
        f'<div style="background:{color};border-radius:4px;height:5px;width:{pct}%;transition:width .4s"></div>'
        f'</div></div>'
    )


def stat_block(items: list[tuple[str, Any, str]]) -> str:
    """Inline stat grid: list of (label, value, color)."""
    cells = "".join(
        f'<div style="text-align:center;padding:0 12px">'
        f'<div style="color:{c};font-size:20px;font-weight:800;font-family:monospace">{v}</div>'
        f'<div style="color:#7a90b0;font-size:10px;letter-spacing:.8px;margin-top:2px">{l.upper()}</div>'
        f'</div>'
        for l, v, c in items
    )
    return (
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;background:rgba(14,21,37,.7);'
        f'border:1px solid #1e2d44;border-radius:8px;padding:14px 8px;'
        f'justify-content:space-around;margin:8px 0">{cells}</div>'
    )
