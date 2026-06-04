"""Page 4 — Compliance Analysis: OWASP, NIST AI RMF, SLSA, governance."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A2_PATH = Path("output/agent2/agent2-report.json")
st.title("Compliance Analysis — Agent 2")
st.caption("NIST AI RMF · OWASP ASVS · OWASP LLM Top 10 · SLSA · Rules governance · Remediation coverage.")

a2: dict = {}
if A2_PATH.exists():
    a2 = json.loads(A2_PATH.read_text(encoding="utf-8"))

if not a2:
    st.info("No Agent 2 report found. Run the analysis from the home page.")
    st.stop()

cr = a2.get("compliance_report", [])

tabs = st.tabs(["Compliance Table", "NIST AI RMF", "SLSA Levels", "Recommendations"])

with tabs[0]:
    st.subheader("Compliance Report — all skills")
    st.dataframe(cr, use_container_width=True)
    if cr:
        avg_score = sum(r.get("compliance_score", 0) for r in cr) / len(cr)
        st.metric("Average Compliance Score", f"{avg_score:.1f}")

with tabs[1]:
    st.subheader("NIST AI RMF Mapping")
    st.caption("GOVERN · MAP · MEASURE · MANAGE — assessed per skill")
    funcs = ["GOVERN", "MAP", "MEASURE", "MANAGE"]
    for func in funcs:
        passing = sum(1 for r in cr if r.get("nist_ai_rmf", {}).get(func) == "pass")
        total = len(cr)
        pct = round(passing / max(total, 1) * 100)
        status = "✓" if pct >= 80 else "⚠"
        st.write(f"{status} **{func}**: {passing}/{total} skills pass ({pct}%)")
    with st.expander("Per-skill NIST AI RMF detail"):
        for r in cr:
            nist = r.get("nist_ai_rmf", {})
            if nist:
                st.write(f"**{r['skill']}**: " + "  ".join(f"{k}={'✓' if v == 'pass' else '⚠'}" for k, v in nist.items()))

with tabs[2]:
    st.subheader("SLSA Levels")
    levels = {1: [], 2: [], 3: []}
    for r in cr:
        lvl = min(r.get("slsa_level", 1), 3)
        levels[lvl].append(r["skill"])
    for lvl, skills in levels.items():
        if skills:
            st.write(f"**SLSA Level {lvl}** ({len(skills)} skills): {', '.join(skills)}")

with tabs[3]:
    st.subheader("Recommendations")
    for rec in a2.get("recommendations", []):
        st.write(f"- {rec}")
    st.subheader("Skills needing compliance review")
    needs_review = [r["skill"] for r in cr if r.get("compliance_posture") not in {"good", "pass"}]
    if needs_review:
        for s in needs_review:
            st.write(f"- {s}")
    else:
        st.success("All skills have acceptable compliance posture.")
