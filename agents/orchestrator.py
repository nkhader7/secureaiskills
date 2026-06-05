"""
Final Orchestrator - runs validation modules in parallel and merges outputs.
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


def _token_rows(r1: dict[str, Any], r2: dict[str, Any], r3: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add_llm_rows(source: dict[str, Any], step: str) -> None:
        for result in source.get("skill_results", []):
            if "error" in result:
                continue
            llm = result.get("llm", {})
            prompt = int(llm.get("prompt_tokens", 0) or 0)
            completion = int(llm.get("completion_tokens", 0) or 0)
            rows.append(
                {
                    "skill": result.get("skill", "unknown"),
                    "step": step,
                    "format": "llm-json",
                    "prompt_tokens": prompt,
                    "completion_tokens": completion,
                    "context_tokens": prompt + completion,
                    "source": step,
                }
            )

    add_llm_rows(r1, "structure_and_function_validation")
    add_llm_rows(r2, "security_and_compliance_validation")
    add_llm_rows(r3, "test_generation_and_execution_validation")

    for bench in r3.get("benchmark_report", []):
        skill = bench.get("skill", "unknown")
        rows.extend(
            [
                {
                    "skill": skill,
                    "step": "original_skill_prompt",
                    "format": "markdown",
                    "prompt_tokens": int(bench.get("original_prompt_tokens", 0) or 0),
                    "completion_tokens": 0,
                    "context_tokens": int(bench.get("original_prompt_tokens", 0) or 0),
                    "source": "benchmark",
                },
                {
                    "skill": skill,
                    "step": "report_template_context",
                    "format": "markdown-template",
                    "prompt_tokens": int(bench.get("template_tokens", 0) or 0),
                    "completion_tokens": 0,
                    "context_tokens": int(bench.get("template_tokens", 0) or 0),
                    "source": "benchmark",
                },
            ]
        )
        for fmt in bench.get("formats", []):
            tokens = int(fmt.get("prompt_tokens", 0) or 0)
            rows.append(
                {
                    "skill": skill,
                    "step": "converted_format_context",
                    "format": fmt.get("format", "unknown"),
                    "prompt_tokens": tokens,
                    "completion_tokens": 0,
                    "context_tokens": int(fmt.get("context_tokens", tokens) or tokens),
                    "compression_opportunity_tokens": int(fmt.get("compression_opportunity_tokens", 0) or 0),
                    "source": "benchmark",
                }
            )

    return rows


def _token_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_prompt = sum(int(r.get("prompt_tokens", 0) or 0) for r in rows)
    total_completion = sum(int(r.get("completion_tokens", 0) or 0) for r in rows)
    total_context = sum(int(r.get("context_tokens", 0) or 0) for r in rows)
    by_step: dict[str, int] = {}
    for row in rows:
        step = str(row.get("step", "unknown"))
        by_step[step] = by_step.get(step, 0) + int(row.get("context_tokens", 0) or 0)
    largest = max(rows, key=lambda r: int(r.get("context_tokens", 0) or 0), default={})
    return {
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_context_tokens": total_context,
        "tokens_by_step": by_step,
        "largest_step": largest,
    }


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

    token_report = _token_rows(r1, r2, r3)
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
        "token_report": token_report,
        "token_summary": _token_summary(token_report),

        "gap_analysis": r1.get("gap_analysis", {}),
        "risk_summary": r2.get("risk_summary", {}),
        "coverage_map": r1.get("coverage_map", {}),

        "recommendations": sorted(
            set(r1.get("recommendations", []))
            | set(r2.get("recommendations", []))
            | set(r3.get("recommendations", []))
        ),

        "downloadable_json": "output/full-report.json",
        "module_reports": {
            "structure": "output/agent1/agent1-report.json",
            "security": "output/agent2/agent2-report.json",
            "validation": "output/agent3/agent3-report.json",
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
