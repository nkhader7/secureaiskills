"""
Final Orchestrator — runs Agent 1, 2, and 3 in parallel and merges outputs.
"""
from __future__ import annotations

import asyncio
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.llm import LocalLLMClient
from agents.agent1 import run_agent1
from agents.agent2 import run_agent2
from agents.agent3 import run_agent3
from agents.schemas import score_summary

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_all(
    skills_dir: str = "skills",
    skills: list[str] | None = None,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
) -> dict[str, Any]:
    llm = LocalLLMClient.from_env_file(REPO_ROOT)

    r1, r2, r3 = await asyncio.gather(
        run_agent1(skills_dir, str(Path(output_dir) / "agent1"), skills, llm),
        run_agent2(skills_dir, str(Path(output_dir) / "agent2"), skills, llm),
        run_agent3(skills_dir, str(Path(output_dir) / "agent3"), skills, llm),
    )

    report = _merge(r1, r2, r3)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "full-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _merge(r1: dict[str, Any], r2: dict[str, Any], r3: dict[str, Any]) -> dict[str, Any]:
    decisions = [r["ci_cd"]["decision"] for r in r3.get("skill_results", [])]
    overall_risk = r2.get("overall_risk", "low")
    confidence = round(
        statistics.mean([
            r1.get("confidence", 0),
            r2.get("confidence", 0),
            r3.get("confidence", 0),
        ]),
        2,
    )

    report = {
        "orchestrator": "secureai-skills",
        "generated_at": _now_utc(),
        "schema_version": "1.0",
        "skills_analyzed": r1.get("skills_analyzed", 0),
        "confidence": confidence,
        "overall_risk": overall_risk,
        "pass_fail_decision": "pass" if all(d == "pass" for d in decisions) and overall_risk != "high" else "fail",

        "executive_report": r3.get("executive_report", []),
        "security_report": r2.get("security_report", []),
        "compliance_report": r2.get("compliance_report", []),
        "coverage_report": r1.get("coverage_report", []),
        "benchmark_report": r3.get("benchmark_report", []),
        "test_report": r3.get("test_report", []),
        "ci_cd_report": r3.get("ci_cd_report", []),
        "graph_artifacts": r3.get("graph_artifacts", {}),

        "gap_analysis": r1.get("gap_analysis", {}),
        "risk_summary": r2.get("risk_summary", {}),
        "coverage_map": r1.get("coverage_map", {}),

        "recommendations": sorted(
            set(r1.get("recommendations", []))
            | set(r2.get("recommendations", []))
            | set(r3.get("recommendations", []))
        ),

        "downloadable_json": "output/full-report.json",
        "agent_reports": {
            "agent1": "output/agent1/agent1-report.json",
            "agent2": "output/agent2/agent2-report.json",
            "agent3": "output/agent3/agent3-report.json",
        },
        "streamlit_dashboard": "app.py",
    }
    scores = score_summary(report)
    report.update(scores)
    report["summary"] = {
        "skills_analyzed": report["skills_analyzed"],
        "overall_risk": report["overall_risk"],
        "pass_fail": report["pass_fail_decision"],
        **scores,
    }
    report["pass_fail"] = report["pass_fail_decision"]
    return report
