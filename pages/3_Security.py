"""Page 3 — Security Analysis: Agent 2 security findings and AI risk."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

A2_PATH = Path("output/agent2/agent2-report.json")
st.title("Security Analysis — Agent 2")
st.caption("Prompt injection, unsafe instructions, secrets, supply chain, AI security (OWASP LLM Top 10).")

a2: dict = {}
if A2_PATH.exists():
    a2 = json.loads(A2_PATH.read_text(encoding="utf-8"))

if not a2:
    st.info("No Agent 2 report found. Run the analysis from the home page.")
    st.stop()

sr = a2.get("security_report", [])
rs = a2.get("risk_summary", {})
findings = a2.get("all_findings", [])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall Risk", str(a2.get("overall_risk", "—")).upper())
c2.metric("High Risk Skills", rs.get("high", 0))
c3.metric("Medium Risk", rs.get("medium", 0))
c4.metric("Total Findings", a2.get("total_findings", 0))

tabs = st.tabs(["Security Report", "AI Security (LLM Top 10)", "Supply Chain", "Findings", "Per-Skill Detail"])

with tabs[0]:
    st.subheader("Security Report — all skills")
    st.dataframe(sr, use_container_width=True)

with tabs[1]:
    st.subheader("OWASP LLM Top 10 — AI Security")
    for r in a2.get("skill_results", []):
        if "error" in r:
            continue
        ai_sec = r.get("security", {}).get("ai_security", {})
        if not ai_sec:
            continue
        triggered = ai_sec.get("triggered_count", 0)
        if triggered > 0:
            with st.expander(f"**{r['skill']}** — {triggered} LLM risk(s) triggered"):
                for cat_id, cat in ai_sec.get("categories", {}).items():
                    if cat["status"] == "fail":
                        st.write(f"**{cat_id} — {cat['name']}**")
                        for f in cat["findings"][:3]:
                            st.write(f"  - {f}")
    st.caption("Skills with no LLM Top 10 findings are omitted.")

with tabs[2]:
    st.subheader("Supply Chain Analysis")
    for r in a2.get("skill_results", []):
        if "error" in r:
            continue
        sc = r.get("governance", {}).get("supply_chain", {})
        if sc.get("external_reference_count", 0) > 0:
            st.write(f"**{r['skill']}** — {sc['external_reference_count']} external reference(s): {sc['external_references']}")

with tabs[3]:
    st.subheader("All Findings")
    if findings:
        for f in findings[:50]:
            st.write(f"- {f}")
        if len(findings) > 50:
            st.caption(f"… and {len(findings) - 50} more.")
    else:
        st.success("No security findings detected.")

with tabs[4]:
    st.subheader("Per-Skill Security Detail")
    skill_names = [r["skill"] for r in a2.get("skill_results", []) if "error" not in r]
    if skill_names:
        selected = st.selectbox("Select skill", skill_names)
        row = next(r for r in a2["skill_results"] if r.get("skill") == selected)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Overall Risk:**", row["overall_risk"].upper())
            st.write("**Prompt Injection:**", row["security"]["prompt_injection"]["risk_level"])
            st.write("**Unsafe Instructions:**", row["security"]["unsafe_instructions"]["found"])
            st.write("**Secret Exposure:**", row["security"]["secret_exposure"]["found"])
        with col2:
            perm = row["security"]["permissions"]
            st.write("**Network Access Required:**", perm.get("network_access_required"))
            st.write("**Filesystem Write:**", perm.get("filesystem_write_required"))
            ai = row["security"].get("ai_security", {})
            st.write("**LLM Risk Level:**", ai.get("risk_level", "—"))
        with st.expander("Full security detail"):
            st.json(row["security"])
