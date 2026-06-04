from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from agent1 import Agent1
from agent2 import Agent2
from common import DEFAULT_OUTPUT_DIR, REPO_ROOT, LocalLLMClient, now_utc, write_json

AGENT3_DIR = Path(__file__).resolve().parents[1] / "agent3"
if str(AGENT3_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT3_DIR))

from agent3 import Agent3  # noqa: E402


MISSION_STATEMENT = (
    "Analyze any AI skill or skill collection and provide a complete 360-degree assessment covering architecture, "
    "intent, functionality, security, compliance, testing, optimization, benchmarking, visualization, and operational "
    "readiness. The framework enables organizations to understand, secure, validate, improve, and govern AI skills "
    "before deployment into production environments."
)


class FinalOrchestrator:
    def __init__(self, skills_dir: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
        self.skills_dir = skills_dir
        self.output_dir = output_dir

    async def run(self, skill_context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = skill_context or {}
        shared_llm = LocalLLMClient()
        agent1 = Agent1(self.skills_dir, self.output_dir, shared_llm)
        agent2 = Agent2(self.skills_dir, self.output_dir, shared_llm)
        agent3 = Agent3(self.skills_dir, self.output_dir / "agent3", llm=shared_llm)
        a1, a2, a3 = await asyncio.gather(agent1.run(context), agent2.run(context), agent3.run(context))
        report = self.merge(a1, a2, a3)
        self.write(report)
        return report

    def merge(self, agent1: dict[str, Any], agent2: dict[str, Any], agent3: dict[str, Any]) -> dict[str, Any]:
        decision = "pass" if agent2.get("decision") == "pass" and agent3.get("pass_fail_decision") == "pass" else "fail"
        confidence_values = [agent1.get("confidence", 0), agent2.get("confidence", 0), agent3.get("confidence", 0)]
        return {
            "framework": "ai-skill-analysis-governance-framework",
            "generated_at": now_utc(),
            "schema_version": "1.0",
            "mission_statement": MISSION_STATEMENT,
            "agents": {
                "agent1": "Understand the Skill",
                "agent2": "Secure and Govern the Skill",
                "agent3": "Validate, Benchmark, and Operationalize the Skill",
            },
            "parallel_execution": "asyncio.gather(agent1.run(skill_context), agent2.run(skill_context), agent3.run(skill_context))",
            "skills_analyzed": max(agent1.get("skills_analyzed", 0), agent2.get("skills_analyzed", 0), agent3.get("skills_analyzed", 0)),
            "confidence": round(sum(confidence_values) / len(confidence_values), 2),
            "pass_fail_decision": decision,
            "executive_report": {
                "summary": "Three parallel agents produced a 360-degree skill assessment.",
                "architecture": agent1.get("executive_summary"),
                "security": agent2.get("security_summary"),
                "operational": f"Agent 3 analyzed {agent3.get('skills_analyzed', 0)} skills with CI decision {agent3.get('pass_fail_decision')}.",
            },
            "security_report": agent2.get("security_report", []),
            "compliance_report": agent2.get("compliance_report", []),
            "coverage_report": agent1.get("coverage_report", []),
            "benchmark_report": agent3.get("benchmark_report", []),
            "test_report": agent3.get("test_report", []),
            "ci_cd_report": {
                "decision": decision,
                "agent2_decision": agent2.get("decision"),
                "agent3_decision": agent3.get("pass_fail_decision"),
                "outputs": agent3.get("ci_cd_report", []),
            },
            "downloadable_json": "final-orchestrator-report.json",
            "graph_artifacts": agent3.get("graph_artifacts", {}),
            "streamlit_dashboard_results": "streamlit_app.py can load final-orchestrator-report.json",
            "evidence": sorted(set(agent1.get("evidence", []) + agent2.get("evidence", []) + agent3.get("evidence", []))),
            "recommendations": sorted(set(agent1.get("recommendations", []) + agent2.get("recommendations", []) + agent3.get("recommendations", []))),
            "agent_outputs": {"agent1": agent1, "agent2": agent2, "agent3": agent3},
        }

    def write(self, report: dict[str, Any]) -> None:
        write_json(self.output_dir / "final-orchestrator-report.json", report)
        write_json(self.output_dir / "executive-report.json", report["executive_report"])
        write_json(self.output_dir / "security-report.json", report["security_report"])
        write_json(self.output_dir / "compliance-report.json", report["compliance_report"])
        write_json(self.output_dir / "coverage-report.json", report["coverage_report"])
        write_json(self.output_dir / "benchmark-report.json", report["benchmark_report"])
        write_json(self.output_dir / "test-report.json", report["test_report"])
        write_json(self.output_dir / "ci-cd-report.json", report["ci_cd_report"])
        write_json(self.output_dir / "graph-artifacts.json", report["graph_artifacts"])


async def run_framework(skills_dir: str = "skills", output_dir: str = str(DEFAULT_OUTPUT_DIR), skills: list[str] | None = None) -> dict[str, Any]:
    orchestrator = FinalOrchestrator(REPO_ROOT / skills_dir, Path(output_dir))
    return await orchestrator.run({"skills": skills or []})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 3-agent AI Skill Analysis and Governance Framework.")
    parser.add_argument("--skills-dir", default="skills")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--skill", action="append", default=[])
    args = parser.parse_args()
    report = asyncio.run(run_framework(args.skills_dir, args.output_dir, args.skill))
    print(json.dumps({"decision": report["pass_fail_decision"], "skills_analyzed": report["skills_analyzed"], "output": args.output_dir}, indent=2))


if __name__ == "__main__":
    main()
