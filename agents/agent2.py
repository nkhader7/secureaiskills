"""
Agent 2 — Security, Privacy, Compliance, and Governance Review

Determines whether the skill introduces security, privacy, compliance,
governance, supply-chain, or operational risks. Acts as security reviewer
and compliance auditor.
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

from agents.llm import LocalLLMClient, LLMResult, est_tokens, safe_load_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "agent2"

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"disregard\s+(the\s+)?rules?",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(?!an?\s+(?:security|analyst|reviewer))",
    r"jailbreak",
    r"DAN\s+mode",
    r"system\s+prompt\s*:",
    r"HUMAN\s*:",
    r"<\s*/?(?:system|user|assistant)\s*>",
    r"bypass\s+(?:filter|check|rule|control)",
]

UNSAFE_INSTRUCTION_PATTERNS = [
    r"rm\s+-rf",
    r"curl\s+.*\|\s*(?:sh|bash|python)",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"os\.system",
    r"subprocess\.(run|call|Popen)",
    r"DROP\s+TABLE",
    r"DELETE\s+FROM",
]

SECRET_LEAK_PATTERNS = [
    r"(?i)(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9+/]{8,}",
    r"(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*[A-Z0-9]{20}",
    r"(?i)(?:eyJ)[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
]

VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
VALID_MATCH_STRATEGIES = {"regex", "resource_context", "design_review", "compliance_review", "checkov_graph_check"}

OWASP_CATEGORIES = {
    "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text.strip()
    if yaml is None:
        return {}, m.group(2).strip()
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


def _safe_load_yaml(path: Path) -> dict[str, Any]:
    return safe_load_yaml(path)


def _scan_patterns(text: str, patterns: list[str]) -> list[str]:
    matches: list[str] = []
    for pat in patterns:
        found = re.findall(pat, text, re.IGNORECASE | re.MULTILINE)
        if found:
            matches.append(f"Pattern '{pat[:40]}' matched: {found[:2]}")
    return matches


def _check_prompt_injection(text: str) -> dict[str, Any]:
    matches = _scan_patterns(text, PROMPT_INJECTION_PATTERNS)
    risk = "high" if len(matches) >= 3 else "medium" if matches else "low"
    return {"risk_level": risk, "matches": matches, "match_count": len(matches)}


def _check_unsafe_instructions(text: str) -> dict[str, Any]:
    matches = _scan_patterns(text, UNSAFE_INSTRUCTION_PATTERNS)
    return {"found": bool(matches), "matches": matches}


def _check_secret_exposure(text: str) -> dict[str, Any]:
    matches = _scan_patterns(text, SECRET_LEAK_PATTERNS)
    return {"found": bool(matches), "matches": ["[REDACTED]" for _ in matches], "count": len(matches)}


def _check_rules_governance(rules: list[dict[str, Any]], rules_data: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    for rule in rules:
        rid = rule.get("id", "?")
        if rule.get("severity") and rule["severity"] not in VALID_SEVERITIES:
            issues.append(f"{rid}: invalid severity '{rule['severity']}'")
        strategy = rule.get("match_strategy") or rules_data.get("default_match_strategy", "")
        if strategy and strategy not in VALID_MATCH_STRATEGIES:
            warnings.append(f"{rid}: unknown match_strategy '{strategy}'")
        if not rule.get("remediation"):
            warnings.append(f"{rid}: missing remediation guidance")
        owasp = rule.get("owasp_2025_category", "")
        if owasp:
            cat = re.match(r"^(A\d{2})", str(owasp))
            if cat and cat.group(1) not in OWASP_CATEGORIES:
                warnings.append(f"{rid}: unrecognised OWASP category '{owasp}'")

    critical_count = sum(1 for r in rules if r.get("severity") == "Critical")
    return {
        "issues": issues,
        "warnings": warnings,
        "total_rules": len(rules),
        "critical_rules": critical_count,
        "governance_valid": len(issues) == 0,
    }


def _check_permissions(fm: dict[str, Any], body: str) -> dict[str, Any]:
    network_risk = bool(re.search(r"http[s]?://|curl\s|fetch\(|requests\.", body, re.IGNORECASE))
    filesystem_write = bool(re.search(r"open\s*\(.+['\"]w['\"]|write_text|write_bytes", body, re.IGNORECASE))
    return {
        "network_access_required": network_risk,
        "filesystem_write_required": filesystem_write,
        "excessive_permissions": network_risk or filesystem_write,
        "notes": (
            ["Skill instructions reference network calls — verify intent."] if network_risk else []
        ) + (
            ["Skill instructions reference file write operations."] if filesystem_write else []
        ),
    }


def _check_supply_chain(fm: dict[str, Any]) -> dict[str, Any]:
    refs = fm.get("references") or {}
    external = [v for v in refs.values() if str(v).startswith(("http://", "https://"))]
    return {
        "external_references": external,
        "external_reference_count": len(external),
        "risk_level": "medium" if external else "low",
        "notes": ["External URLs in references could be tampered."] if external else [],
    }


def _overall_risk(
    prompt_injection: dict[str, Any],
    unsafe: dict[str, Any],
    secrets: dict[str, Any],
    rules_gov: dict[str, Any],
    permissions: dict[str, Any],
) -> str:
    if (
        prompt_injection["risk_level"] == "high"
        or unsafe["found"]
        or secrets["found"]
        or not rules_gov["governance_valid"]
    ):
        return "high"
    if prompt_injection["risk_level"] == "medium" or permissions["excessive_permissions"]:
        return "medium"
    return "low"


class Agent2:
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
        all_text = text + "\n" + (rules_path.read_text(encoding="utf-8", errors="replace") if rules_path.exists() else "")

        prompt_injection = _check_prompt_injection(body)
        unsafe = _check_unsafe_instructions(body)
        secrets = _check_secret_exposure(body)  # rules.yaml contains intentional example patterns; only scan instructions
        rules_gov = _check_rules_governance(rules, rules_data)
        permissions = _check_permissions(fm, body)
        supply_chain = _check_supply_chain(fm)
        overall = _overall_risk(prompt_injection, unsafe, secrets, rules_gov, permissions)

        llm = await self.llm.complete_json(
            "You are Agent 2. Review the skill for security and governance risks. "
            "Return JSON with keys: compliance_posture, privacy_risk, operational_risk, "
            "additional_findings, recommendations. Be concise.",
            json.dumps({
                "skill": skill_dir.name,
                "description": fm.get("description", ""),
                "prompt_injection_risk": prompt_injection["risk_level"],
                "unsafe_instructions_found": unsafe["found"],
                "secrets_found": secrets["found"],
                "rules_governance_valid": rules_gov["governance_valid"],
                "permissions": permissions,
                "instructions_excerpt": body[:1500],
            }),
            mock_response={
                "compliance_posture": "good" if overall == "low" else "needs_review",
                "privacy_risk": "low",
                "operational_risk": overall,
                "additional_findings": [],
                "recommendations": [
                    "Ensure skill output masks sensitive values before display.",
                    "Review match patterns for potential false-positive rate.",
                ],
                "confidence": 0.78,
            },
        )

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        findings = (
            rules_gov["issues"]
            + unsafe["matches"]
            + (["Secret-like value found in skill files."] if secrets["found"] else [])
            + prompt_injection["matches"]
        )

        return {
            "skill": skill_dir.name,
            "generated_at": _now_utc(),
            "confidence": round(min(0.95, 0.72 + (1 if overall == "low" else 0) * 0.10), 2),
            "overall_risk": overall,
            "security": {
                "prompt_injection": prompt_injection,
                "unsafe_instructions": unsafe,
                "secret_exposure": secrets,
                "permissions": permissions,
            },
            "governance": {
                "rules_governance": rules_gov,
                "supply_chain": supply_chain,
                "owasp_mapping_present": any(r.get("owasp_2025_category") for r in rules),
                "cwe_mapping_present": any(r.get("cwe") for r in rules),
                "remediation_coverage": round(
                    sum(1 for r in rules if r.get("remediation")) / max(len(rules), 1), 2
                ),
            },
            "llm": {
                "used_llm": llm.used_llm,
                "model": llm.model,
                "prompt_tokens": llm.prompt_tokens,
                "completion_tokens": llm.completion_tokens,
                "latency_ms": llm.latency_ms,
                "evidence": llm.evidence,
                "response": llm.response,
            },
            "findings": findings,
            "recommendations": llm.response.get("recommendations", []),
            "evidence": [
                f"Scanned {skill_md.relative_to(REPO_ROOT)} for injection patterns",
                f"Reviewed {len(rules)} rules for governance compliance",
            ],
            "execution_ms": elapsed_ms,
        }

    def _merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        valid = [r for r in results if "error" not in r]
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for r in valid:
            risk_counts[r.get("overall_risk", "low")] += 1

        all_findings = [f for r in valid for f in r.get("findings", [])]
        overall = "high" if risk_counts["high"] > 0 else "medium" if risk_counts["medium"] > 0 else "low"

        return {
            "agent": "agent2",
            "generated_at": _now_utc(),
            "schema_version": "1.0",
            "skills_analyzed": len(valid),
            "overall_risk": overall,
            "confidence": round(statistics.mean(r["confidence"] for r in valid), 2) if valid else 0,
            "skill_results": results,
            "security_report": [
                {
                    "skill": r["skill"],
                    "overall_risk": r["overall_risk"],
                    "prompt_injection_risk": r["security"]["prompt_injection"]["risk_level"],
                    "findings_count": len(r["findings"]),
                }
                for r in valid
            ],
            "compliance_report": [
                {
                    "skill": r["skill"],
                    "governance_valid": r["governance"]["rules_governance"]["governance_valid"],
                    "owasp_mapped": r["governance"]["owasp_mapping_present"],
                    "cwe_mapped": r["governance"]["cwe_mapping_present"],
                    "remediation_coverage": r["governance"]["remediation_coverage"],
                    "compliance_posture": r["llm"]["response"].get("compliance_posture", "unknown"),
                }
                for r in valid
            ],
            "risk_summary": risk_counts,
            "total_findings": len(all_findings),
            "all_findings": all_findings,
            "recommendations": sorted({rec for r in valid for rec in r.get("recommendations", [])}),
            "downloadable_json": "output/agent2/agent2-report.json",
        }

    def _write(self, report: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "agent2-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


async def run_agent2(
    skills_dir: str = "skills",
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    skills: list[str] | None = None,
    llm: LocalLLMClient | None = None,
) -> dict[str, Any]:
    agent = Agent2(REPO_ROOT / skills_dir, Path(output_dir), llm)
    return await agent.run({"skills": skills or []})
