"""
Agent 1 — Skill Intelligence, Structure, Intent, and Functional Analysis

Determines what the skill is, why it exists, how it works, what capabilities
it provides, how it is structured, and which phases of the lifecycle it covers.
"""
from __future__ import annotations

import asyncio
import json
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from agents.llm import LocalLLMClient, safe_load_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "agent1"

SKILL_CATEGORY_MAP: dict[str, str] = {
    "detect-secrets": "Secrets Detection",
    "detect-supply-chain-risks": "SCA",
    "scan-for-injection": "SAST",
    "scan-for-xss": "SAST",
    "scan-for-ssrf": "SAST",
    "scan-static-analysis": "SAST",
    "scan-broken-access-control": "SAST",
    "scan-exception-handling": "SAST",
    "scan-api-security": "API Security",
    "scan-iac-security": "IaC Security",
    "scan-kubernetes-manifests": "Kubernetes Security",
    "scan-container-image": "Container Security",
    "scan-security-headers": "SAST",
    "scan-sca-dependencies": "SCA",
    "scan-yaml-security": "Config Security",
    "scan-json-security": "Config Security",
    "scan-xml-security": "Config Security",
    "scan-toml-security": "Config Security",
    "scan-markdown-security": "Config Security",
    "audit-asvs-compliance": "Compliance Validation",
    "audit-auth-session-management": "Compliance Validation",
    "audit-crypto-usage": "Compliance Validation",
    "audit-logging-monitoring": "Compliance Validation",
    "generate-sbom": "SBOM",
    "generate-dependency-graph": "SBOM",
    "threat-model-system": "Threat Modeling",
}

COVERAGE_DOMAINS = [
    "Threat Modeling", "SAST", "DAST", "SCA", "SBOM",
    "IaC Security", "Kubernetes Security", "Container Security",
    "Secrets Detection", "Dependency Scanning", "Compliance Validation",
    "LLM Security", "Prompt Injection Testing", "Runtime Validation",
    "Exploit Validation", "Remediation", "Reporting", "CI/CD Enforcement", "API Security",
]

COVERED_DOMAINS: set[str] = {
    "Threat Modeling", "SAST", "SCA", "SBOM", "IaC Security",
    "Kubernetes Security", "Container Security", "Secrets Detection",
    "Dependency Scanning", "Compliance Validation", "Remediation",
    "Reporting", "API Security", "Config Security",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    text = text.lstrip("\ufeff")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text.strip()
    if yaml is None:
        return {}, m.group(2).strip()
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


def _safe_load_yaml(path: Path) -> dict[str, Any]:
    return safe_load_yaml(path)


def _count_rules(data: dict[str, Any]) -> int:
    return len(data.get("rules", []))


def _extract_match_strategies(rules: list[dict[str, Any]]) -> list[str]:
    return sorted({r.get("match_strategy", "unspecified") for r in rules if r.get("match_strategy")})


def _extract_severities(rules: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in rules:
        sev = r.get("severity", "Unknown")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _validate_skill(
    fm: dict[str, Any],
    body: str,
    rules_data: dict[str, Any],
    skill_dir: Path,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    required_fm = ["name", "description", "triggers", "references"]
    for field in required_fm:
        if not fm.get(field):
            issues.append(f"Frontmatter missing required field: {field}")

    for section in ["## Orchestration", "## Usage"]:
        if section not in body:
            warnings.append(f"SKILL.md body missing section: {section}")

    refs = fm.get("references") or {}
    for ref_key, ref_path in refs.items():
        resolved = skill_dir / ref_path
        if not resolved.exists():
            issues.append(f"Broken reference [{ref_key}]: {ref_path} not found")

    rules = rules_data.get("rules", [])
    if not rules:
        issues.append("rules.yaml contains no rules")
    for rule in rules:
        if not rule.get("remediation"):
            warnings.append(f"Rule {rule.get('id', '?')} missing remediation field")
        if isinstance(rule.get("patterns"), list) and not rule["patterns"]:
            issues.append(f"Rule {rule.get('id', '?')} has empty patterns list")
        sev = rule.get("severity", "")
        if sev and sev not in {"Critical", "High", "Medium", "Low", "Info"}:
            issues.append(f"Rule {rule.get('id', '?')} has invalid severity: {sev}")
        if not rule.get("match_strategy") and not rules_data.get("default_match_strategy"):
            warnings.append(f"Rule {rule.get('id', '?')} missing match_strategy")

    tmpl_path = skill_dir / refs.get("report_template", "references/report-template.md")
    if tmpl_path.exists():
        tmpl = tmpl_path.read_text(encoding="utf-8", errors="replace")
        for placeholder in ["{{target}}", "{{date}}", "{{#each findings}}", "{{#if no_findings}}"]:
            if placeholder not in tmpl:
                warnings.append(f"report-template.md missing placeholder: {placeholder}")
    else:
        issues.append("report-template.md not found")

    return {
        "issues": issues,
        "warnings": warnings,
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "warning_count": len(warnings),
    }


class Agent1:
    def __init__(
        self,
        skills_dir: Path = SKILLS_DIR,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        llm: LocalLLMClient | None = None,
    ) -> None:
        self.skills_dir = skills_dir
        self.output_dir = output_dir
        self.llm = llm or LocalLLMClient.from_env_file(REPO_ROOT)

    async def run(self, skill_context: dict[str, Any] | None = None) -> dict[str, Any]:
        selected = set((skill_context or {}).get("skills") or [])
        skill_dirs = [p for p in sorted(self.skills_dir.iterdir()) if p.is_dir() and not p.name.startswith("_")]
        if selected:
            skill_dirs = [p for p in skill_dirs if p.name in selected]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        results = await asyncio.gather(*(self._analyze(d) for d in skill_dirs))
        report = self._merge(list(results))
        self._write(report)
        return report

    async def analyze_skill_context(self, ctx: Any) -> dict[str, Any]:
        """Analyze a pre-parsed SkillContext (from core.parsers or agents.ingest)."""
        from core.parsers import SkillContext
        if not isinstance(ctx, SkillContext):
            ctx = SkillContext(name=str(ctx), format="unknown", raw_text="")

        rules = ctx.rules
        fm = ctx.frontmatter
        body = ctx.body

        llm = await self.llm.complete_json(
            "You are Agent 1. Analyze the skill and return JSON with keys: "
            "problem_solved, success_criteria, failure_conditions, decision_logic, "
            "execution_phases, data_flow_summary, control_flow_summary. Be concise.",
            json.dumps({"skill": ctx.name, "description": fm.get("description", ""), "instructions_excerpt": body[:2000], "rule_count": len(rules)}),
            mock_response={
                "problem_solved": fm.get("description", "Uploaded skill analysis."),
                "success_criteria": "Skill analyzed and structured report produced.",
                "failure_conditions": ["Missing required fields"],
                "decision_logic": ["Parse", "Evaluate", "Report"],
                "execution_phases": ["load", "evaluate", "report"],
                "data_flow_summary": "Parsed context → LLM evaluation → report",
                "control_flow_summary": "Sequential: parse → evaluate → render",
                "confidence": 0.75,
            },
        )

        from agents.agent1 import _validate_skill, _extract_match_strategies, _extract_severities, SKILL_CATEGORY_MAP
        skill_dir = Path(ctx.skill_dir) if ctx.skill_dir else Path(".")
        validation = _validate_skill(fm, body, ctx.rules_data, skill_dir)
        category = SKILL_CATEGORY_MAP.get(ctx.name, "General Security")

        return {
            "skill": ctx.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "confidence": round(min(0.95, 0.70 + min(len(rules), 30) / 100), 2),
            "discovery": {"name": ctx.name, "category": category, "format": ctx.format, "framework": "LLM-native"},
            "structure": {
                "inputs": ["target path", "flags"],
                "outputs": ["structured findings", "severity summary", "report"],
                "rule_count": len(rules),
                "match_strategies": _extract_match_strategies(rules),
                "severity_distribution": _extract_severities(rules),
            },
            "functional": llm.response,
            "validation": validation,
            "llm": {"used_llm": llm.used_llm, "model": llm.model, "evidence": llm.evidence},
            "evidence": [f"Parsed uploaded skill: {ctx.name} (format={ctx.format}, rules={len(rules)})"],
            "execution_ms": 0,
        }

    async def _analyze(self, skill_dir: Path) -> dict[str, Any]:
        started = time.perf_counter()
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return {"skill": skill_dir.name, "error": "SKILL.md not found"}

        text = skill_md.read_text(encoding="utf-8", errors="replace")
        fm, body = _parse_frontmatter(text)
        refs = fm.get("references") or {}
        rules_path = skill_dir / refs.get("rules", "references/rules.yaml")
        rules_data = _safe_load_yaml(rules_path)
        rules = rules_data.get("rules", [])

        llm = await self.llm.complete_json(
            "You are Agent 1. Analyze the skill and return JSON with keys: "
            "problem_solved, success_criteria, failure_conditions, decision_logic, "
            "execution_phases, data_flow_summary, control_flow_summary. Be concise.",
            json.dumps({
                "skill": skill_dir.name,
                "description": fm.get("description", ""),
                "instructions_excerpt": body[:2000],
                "rule_count": len(rules),
                "rules_sample": rules[:3],
            }),
            mock_response={
                "problem_solved": fm.get("description", "Security analysis of target files."),
                "success_criteria": "Findings emitted with file, line, rule_id, severity, snippet, and remediation.",
                "failure_conditions": ["SKILL.md missing", "rules.yaml empty", "target has no matching files"],
                "decision_logic": ["Load rules", "Identify target files", "Evaluate each file × rule", "Aggregate by severity"],
                "execution_phases": ["load", "assemble", "evaluate", "report"],
                "data_flow_summary": "Disk → LLM context → evaluated findings → Markdown report",
                "control_flow_summary": "Sequential: load → identify → evaluate → aggregate → render",
                "confidence": 0.80,
            },
        )

        validation = _validate_skill(fm, body, rules_data, skill_dir)
        category = SKILL_CATEGORY_MAP.get(skill_dir.name, "General Security")
        severity_dist = _extract_severities(rules)
        match_strategies = _extract_match_strategies(rules)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        return {
            "skill": skill_dir.name,
            "generated_at": _now_utc(),
            "confidence": round(min(0.95, 0.70 + min(len(rules), 30) / 100), 2),
            "discovery": {
                "name": fm.get("name", skill_dir.name),
                "category": category,
                "type": "detection" if skill_dir.name.startswith(("scan-", "detect-")) else
                        "audit" if skill_dir.name.startswith("audit-") else
                        "generation" if skill_dir.name.startswith("generate-") else "analysis",
                "framework": "LLM-native",
                "purpose": fm.get("description", ""),
                "triggers": fm.get("triggers", []),
                "intended_audience": ["developers", "AppSec engineers", "CI/CD pipelines"],
                "execution_model": "on-demand invocation; rules loaded fresh per call",
            },
            "structure": {
                "inputs": ["target path (optional)", "flags (optional)", "SKILL.md", "rules.yaml", "report-template.md"],
                "outputs": ["structured findings JSON", "severity summary", "Markdown report"],
                "variables": ["target", "flags"],
                "env_vars": [],
                "references": refs,
                "dependencies": list(refs.values()),
                "rule_count": len(rules),
                "match_strategies": match_strategies,
                "default_match_strategy": rules_data.get("default_match_strategy", "unspecified"),
                "severity_distribution": severity_dist,
                "rules_bytes": rules_path.stat().st_size if rules_path.exists() else 0,
                "rules_truncated_at_60kb": (rules_path.stat().st_size > 60_000) if rules_path.exists() else False,
            },
            "functional": llm.response,
            "validation": validation,
            "llm": {
                "used_llm": llm.used_llm,
                "model": llm.model,
                "prompt_tokens": llm.prompt_tokens,
                "completion_tokens": llm.completion_tokens,
                "latency_ms": llm.latency_ms,
                "evidence": llm.evidence,
            },
            "evidence": [
                f"Read {skill_md.relative_to(REPO_ROOT)}",
                f"Read {rules_path.relative_to(REPO_ROOT) if rules_path.exists() else str(rules_path)} ({len(rules)} rules)",
            ],
            "execution_ms": elapsed_ms,
        }

    def _merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        valid = [r for r in results if "error" not in r]
        all_issues = [i for r in valid for i in r.get("validation", {}).get("issues", [])]
        covered = {r["discovery"]["category"] for r in valid}
        missing_domains = [d for d in COVERAGE_DOMAINS if d not in COVERED_DOMAINS]
        coverage_score = round(len(COVERED_DOMAINS & set(COVERAGE_DOMAINS)) / len(COVERAGE_DOMAINS), 2)

        return {
            "agent": "agent1",
            "generated_at": _now_utc(),
            "schema_version": "1.0",
            "skills_analyzed": len(valid),
            "confidence": round(statistics.mean(r["confidence"] for r in valid), 2) if valid else 0,
            "skill_results": results,
            "coverage_report": [
                {
                    "skill": r["skill"],
                    "category": r["discovery"]["category"],
                    "type": r["discovery"]["type"],
                    "rules": r["structure"]["rule_count"],
                    "valid": r["validation"]["valid"],
                    "issues": r["validation"]["issue_count"],
                    "warnings": r["validation"]["warning_count"],
                }
                for r in valid
            ],
            "dependency_map": {
                r["skill"]: r["structure"]["dependencies"] for r in valid
            },
            "execution_flow": [
                "User invokes skill",
                "SKILL.md loaded (frontmatter + orchestration body)",
                "rules.yaml loaded (capped at 60 KB)",
                "Target files identified (git diff or user path)",
                "LLM evaluates each file × rule using match_strategy",
                "Findings aggregated by severity",
                "report-template.md populated with findings",
                "Markdown report streamed to user",
            ],
            "coverage_map": {
                "covered_domains": sorted(covered),
                "missing_domains": missing_domains,
                "coverage_score": coverage_score,
            },
            "gap_analysis": {
                "validation_issues": all_issues,
                "uncovered_domains": missing_domains,
                "skills_with_issues": [r["skill"] for r in valid if not r["validation"]["valid"]],
                "total_issues": len(all_issues),
            },
            "recommendations": [
                "Add scan-llm-security skill to cover LLM/AI model security domain.",
                "Add scan-prompt-injection skill to cover prompt injection testing.",
                "Add enforce-security-gate skill to support CI/CD enforcement.",
                "Consider splitting scan-iac-security (1,746 rules) to avoid 60 KB truncation.",
                "Add HOST/PORT env var support to the API server for containerized deployments.",
            ],
            "downloadable_json": "output/agent1/agent1-report.json",
        }

    def _write(self, report: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "agent1-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


async def run_agent1(
    skills_dir: str = "skills",
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    skills: list[str] | None = None,
    llm: LocalLLMClient | None = None,
) -> dict[str, Any]:
    agent = Agent1(REPO_ROOT / skills_dir, Path(output_dir), llm)
    return await agent.run({"skills": skills or []})
