from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

from common import DEFAULT_OUTPUT_DIR, REPO_ROOT, LocalLLMClient, est_tokens, load_skill, now_utc, skill_dirs, write_json


LIFECYCLE_KEYWORDS = {
    "design": ["threat", "design", "architecture", "asvs", "access control", "auth"],
    "development": ["scan", "detect", "code", "static", "xss", "injection", "secret"],
    "supply_chain": ["dependency", "sbom", "supply", "sca", "container"],
    "operations": ["logging", "monitoring", "headers", "kubernetes", "iac"],
    "compliance": ["asvs", "owasp", "audit", "compliance"],
}


class Agent1:
    def __init__(self, skills_dir: Path, output_dir: Path = DEFAULT_OUTPUT_DIR, llm: LocalLLMClient | None = None) -> None:
        self.skills_dir = skills_dir
        self.output_dir = output_dir
        self.llm = llm or LocalLLMClient()

    async def run(self, skill_context: dict[str, Any] | None = None) -> dict[str, Any]:
        selected = (skill_context or {}).get("skills") or []
        results = await asyncio.gather(*(self.analyze(path) for path in skill_dirs(self.skills_dir, selected)))
        report = self.merge(results)
        write_json(self.output_dir / "agent1" / "agent1-report.json", report)
        return report

    async def analyze(self, skill_dir: Path) -> dict[str, Any]:
        skill = load_skill(skill_dir)
        text = f"{skill['name']} {skill['frontmatter'].get('description', '')} {skill['body']}".lower()
        lifecycle = [phase for phase, terms in LIFECYCLE_KEYWORDS.items() if any(term in text for term in terms)]
        sections = re.findall(r"^##\s+(.+)$", skill["body"], re.MULTILINE)
        orchestration_steps = re.findall(r"^\d+\.\s+(.+)$", skill["body"], re.MULTILINE)
        capabilities = self.capabilities(skill)
        completeness_checks = self.completeness(skill, sections, orchestration_steps)
        llm = await self.llm.complete_json(
            "You are Agent 1. Return concise JSON about skill intent, architecture, and completeness.",
            __import__("json").dumps(
                {
                    "skill": skill["name"],
                    "description": skill["frontmatter"].get("description", ""),
                    "sections": sections,
                    "rule_count": len(skill["rules"]),
                    "orchestration_steps": orchestration_steps[:8],
                },
                indent=2,
            ),
        )
        return {
            "skill": skill["name"],
            "agent": "agent1",
            "generated_at": now_utc(),
            "intent": skill["frontmatter"].get("description", skill["body"].split("\n", 1)[0]),
            "architecture": {
                "entrypoint": str(Path(skill["skill_md"]).relative_to(REPO_ROOT)),
                "rules": str(Path(skill["rules_path"]).relative_to(REPO_ROOT)),
                "report_template": str(Path(skill["template_path"]).relative_to(REPO_ROOT)),
                "sections": sections,
                "rule_count": len(skill["rules"]),
                "default_match_strategy": skill["rules_data"].get("default_match_strategy", "unspecified"),
            },
            "capabilities": capabilities,
            "inputs": ["target path", "changed files", "flags", "rule catalog", "report template"],
            "outputs": ["findings", "severity summary", "evidence", "remediation", "markdown or JSON report"],
            "dependencies": list(skill["references"].values()),
            "execution_flow": orchestration_steps,
            "lifecycle_coverage": lifecycle or ["development"],
            "functional_completeness": completeness_checks,
            "context_profile": {
                "skill_tokens": est_tokens(skill["raw_text"]),
                "rule_tokens": est_tokens(str(skill["rules_data"])),
                "template_tokens": est_tokens(skill["template"]),
            },
            "llm": llm.__dict__,
            "confidence": self.confidence(completeness_checks, len(skill["rules"])),
            "evidence": [
                f"Parsed frontmatter for {skill['name']}",
                f"Found {len(sections)} body sections",
                f"Loaded {len(skill['rules'])} rules",
                *llm.evidence,
            ],
            "recommendations": self.recommendations(completeness_checks, len(orchestration_steps)),
        }

    def capabilities(self, skill: dict[str, Any]) -> list[str]:
        name = skill["name"]
        caps = []
        if name.startswith("detect-"):
            caps.append("risk detection")
        if name.startswith("scan-"):
            caps.append("target scanning")
        if name.startswith("audit-"):
            caps.append("domain audit")
        if name.startswith("generate-"):
            caps.append("artifact generation")
        if skill["rules"]:
            caps.append("rule-driven analysis")
        if skill["template"]:
            caps.append("report rendering")
        return caps or ["skill execution"]

    def completeness(self, skill: dict[str, Any], sections: list[str], steps: list[str]) -> dict[str, Any]:
        refs = skill["references"]
        checks = {
            "has_name": bool(skill["frontmatter"].get("name")),
            "has_description": bool(skill["frontmatter"].get("description")),
            "has_triggers": bool(skill["frontmatter"].get("triggers")),
            "has_orchestration": any(s.lower() == "orchestration" for s in sections),
            "has_usage": any(s.lower() == "usage" for s in sections),
            "has_rules": bool(skill["rules"]),
            "has_report_template": bool(skill["template"]),
            "references_rules": "rules" in refs,
            "references_report_template": "report_template" in refs,
            "has_execution_steps": len(steps) >= 3,
        }
        passed = sum(1 for value in checks.values() if value)
        return {"checks": checks, "score": round(passed / len(checks) * 100, 1), "passed": passed, "total": len(checks)}

    def confidence(self, completeness: dict[str, Any], rule_count: int) -> float:
        return round(min(0.96, 0.55 + completeness["score"] / 250 + min(rule_count, 50) / 500), 2)

    def recommendations(self, completeness: dict[str, Any], step_count: int) -> list[str]:
        recs = []
        checks = completeness["checks"]
        if not checks["has_usage"]:
            recs.append("Add a Usage section with default, path-specific, and all-files invocation examples.")
        if not checks["has_report_template"]:
            recs.append("Add a report template so outputs remain stable across executions.")
        if step_count < 5:
            recs.append("Expand orchestration with target selection, rule loading, evidence capture, and report rendering steps.")
        if not recs:
            recs.append("Maintain the current structured skill contract and keep references versioned.")
        return recs

    def merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        avg = round(sum(r["confidence"] for r in results) / max(len(results), 1), 2)
        return {
            "agent": "agent1",
            "generated_at": now_utc(),
            "skills_analyzed": len(results),
            "confidence": avg,
            "executive_summary": f"Agent 1 analyzed {len(results)} skills for intent, architecture, lifecycle coverage, and completeness.",
            "architecture_report": results,
            "coverage_report": [
                {"skill": r["skill"], "lifecycle_coverage": r["lifecycle_coverage"], "score": r["functional_completeness"]["score"]}
                for r in results
            ],
            "evidence": [e for r in results for e in r["evidence"]],
            "recommendations": sorted({rec for r in results for rec in r["recommendations"]}),
        }
