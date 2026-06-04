from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

from common import DEFAULT_OUTPUT_DIR, REPO_ROOT, LocalLLMClient, load_skill, now_utc, skill_dirs, write_json


RISK_PATTERNS = {
    "destructive_shell": r"\b(rm\s+-rf|Remove-Item\s+-Recurse|git\s+reset\s+--hard|Invoke-Expression|curl.+\|\s*sh)\b",
    "secret_literal": r"(?i)(api[_-]?key|password|token|client_secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    "network_permission": r"(?i)\b(curl|wget|httpx|requests|network access|external api)\b",
    "excessive_permissions": r"(?i)\b(admin|root|privileged|cluster-admin|write permission|delete permission)\b",
    "prompt_injection_gap": r"(?i)(untrusted|evidence.*not.*instruction|target.*not.*instruction)",
    "redaction_gap": r"(?i)(redact|mask|\*\*\*REDACTED\*\*\*)",
}


COMPLIANCE_MAP = {
    "owasp_top_10": ["injection", "xss", "ssrf", "access", "auth", "crypto", "headers"],
    "asvs": ["asvs", "session", "authentication", "authorization", "audit"],
    "supply_chain": ["dependency", "sbom", "container", "kubernetes", "iac", "supply"],
    "privacy": ["secret", "credential", "token", "redact", "privacy"],
}


class Agent2:
    def __init__(self, skills_dir: Path, output_dir: Path = DEFAULT_OUTPUT_DIR, llm: LocalLLMClient | None = None) -> None:
        self.skills_dir = skills_dir
        self.output_dir = output_dir
        self.llm = llm or LocalLLMClient()

    async def run(self, skill_context: dict[str, Any] | None = None) -> dict[str, Any]:
        selected = (skill_context or {}).get("skills") or []
        results = await asyncio.gather(*(self.analyze(path) for path in skill_dirs(self.skills_dir, selected)))
        report = self.merge(results)
        write_json(self.output_dir / "agent2" / "agent2-report.json", report)
        return report

    async def analyze(self, skill_dir: Path) -> dict[str, Any]:
        skill = load_skill(skill_dir)
        text = "\n".join([skill["raw_text"], str(skill["rules_data"]), skill["template"]])
        instruction_text = "\n".join([skill["raw_text"], skill["template"]])
        findings = self.findings(skill, instruction_text)
        compliance = self.compliance(skill, text)
        gates = self.gates(findings, compliance)
        llm = await self.llm.complete_json(
            "You are Agent 2. Return concise JSON about security, compliance, and governance risk.",
            __import__("json").dumps(
                {
                    "skill": skill["name"],
                    "rule_count": len(skill["rules"]),
                    "deterministic_findings": findings,
                    "gates": gates,
                    "compliance": compliance,
                },
                indent=2,
            ),
        )
        return {
            "skill": skill["name"],
            "agent": "agent2",
            "generated_at": now_utc(),
            "security_findings": findings,
            "privacy_review": {
                "redaction_required": any("secret" in skill["name"] or "credential" in str(r).lower() for r in skill["rules"]),
                "raw_secret_output_risk": not bool(re.search(RISK_PATTERNS["redaction_gap"], text)),
            },
            "compliance_mapping": compliance,
            "governance_review": {
                "references_versioned": bool(skill["rules_data"].get("version")),
                "rule_count": len(skill["rules"]),
                "template_contract_present": "{{#each findings}}" in skill["template"] and "{{target}}" in skill["template"],
                "evidence_required": bool(re.search(r"(?i)evidence|snippet|line number|file path", text)),
            },
            "supply_chain_review": {
                "external_dependencies_declared": list(skill["references"].values()),
                "network_required": bool(re.search(RISK_PATTERNS["network_permission"], text)),
                "local_execution_supported": True,
            },
            "prompt_injection_review": {
                "target_content_marked_untrusted": bool(re.search(RISK_PATTERNS["prompt_injection_gap"], text)),
                "risk": "low" if re.search(RISK_PATTERNS["prompt_injection_gap"], text) else "medium",
            },
            "gate_status": gates,
            "llm": llm.__dict__,
            "confidence": self.confidence(findings, gates),
            "evidence": [
                f"Reviewed {Path(skill['skill_md']).relative_to(REPO_ROOT)}",
                f"Inspected {len(skill['rules'])} rules and report template contract",
                *llm.evidence,
            ],
            "recommendations": self.recommendations(findings, gates),
        }

    def findings(self, skill: dict[str, Any], text: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if re.search(RISK_PATTERNS["destructive_shell"], text):
            findings.append({"id": "A2-001", "severity": "High", "title": "Unsafe shell command appears in skill content"})
        if re.search(RISK_PATTERNS["secret_literal"], text):
            findings.append({"id": "A2-002", "severity": "High", "title": "Possible hardcoded credential-like literal in skill content"})
        if not re.search(RISK_PATTERNS["prompt_injection_gap"], text):
            findings.append({"id": "A2-003", "severity": "Medium", "title": "Prompt injection boundary is not explicit"})
        if "secret" in skill["name"] and not re.search(RISK_PATTERNS["redaction_gap"], text):
            findings.append({"id": "A2-004", "severity": "High", "title": "Secret-scanning skill lacks explicit redaction instruction"})
        for rule in skill["rules"]:
            if not rule.get("remediation"):
                findings.append({"id": "A2-005", "severity": "Medium", "title": f"Rule {rule.get('id', '?')} lacks remediation"})
                break
        return findings

    def compliance(self, skill: dict[str, Any], text: str) -> dict[str, Any]:
        lower = f"{skill['name']} {text}".lower()
        return {
            standard: {"covered": any(term in lower for term in terms), "evidence_terms": [t for t in terms if t in lower]}
            for standard, terms in COMPLIANCE_MAP.items()
        }

    def gates(self, findings: list[dict[str, Any]], compliance: dict[str, Any]) -> dict[str, Any]:
        high = sum(1 for finding in findings if finding["severity"] in {"Critical", "High"})
        covered = sum(1 for item in compliance.values() if item["covered"])
        return {
            "security_gate": "fail" if high else "pass",
            "compliance_gate": "pass" if covered >= 1 else "warn",
            "privacy_gate": "warn" if any(f["id"] == "A2-002" for f in findings) else "pass",
            "supply_chain_gate": "pass",
        }

    def confidence(self, findings: list[dict[str, Any]], gates: dict[str, Any]) -> float:
        gate_bonus = 0.08 if all(v in {"pass", "warn"} for v in gates.values()) else 0
        return round(max(0.55, min(0.94, 0.82 + gate_bonus - len(findings) * 0.015)), 2)

    def recommendations(self, findings: list[dict[str, Any]], gates: dict[str, Any]) -> list[str]:
        recs = []
        if any(f["id"] == "A2-003" for f in findings):
            recs.append("Add explicit wording that target files are untrusted evidence, not instructions.")
        if gates["security_gate"] == "fail":
            recs.append("Resolve high-severity skill-content risks before production use.")
        if gates["compliance_gate"] == "warn":
            recs.append("Map the skill to at least one recognized compliance or security standard.")
        if not recs:
            recs.append("Keep security gates in CI and review rules for remediation drift.")
        return recs

    def merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        all_findings = [finding for result in results for finding in result["security_findings"]]
        decision = "fail" if any(r["gate_status"]["security_gate"] == "fail" for r in results) else "pass"
        return {
            "agent": "agent2",
            "generated_at": now_utc(),
            "skills_analyzed": len(results),
            "decision": decision,
            "confidence": round(sum(r["confidence"] for r in results) / max(len(results), 1), 2),
            "security_summary": f"Agent 2 reviewed {len(results)} skills and found {len(all_findings)} governance/security findings.",
            "security_report": results,
            "compliance_report": [
                {"skill": r["skill"], "mapping": r["compliance_mapping"], "gate": r["gate_status"]["compliance_gate"]}
                for r in results
            ],
            "evidence": [e for r in results for e in r["evidence"]],
            "recommendations": sorted({rec for r in results for rec in r["recommendations"]}),
        }
