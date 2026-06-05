"""
Agent 2 — Security Skill Validator

Validates every AI security testing skill against industry security standards:
  • OWASP Top 10 2025           • OWASP ASVS 5.0
  • CWE Top 25 (2024)           • OWASP LLM Top 10
  • NIST AI RMF (GOVERN/MAP/MEASURE/MANAGE)
  • NIST SSDF                   • SLSA Framework
  • CIS Controls v8

For each skill the agent checks:
  1. Rule quality   — id, severity, description, patterns, CWE, OWASP, remediation, CAPEC
  2. OWASP coverage — which A01-A10 categories are addressed
  3. CWE coverage   — which CWEs are covered vs. expected for the domain
  4. Attack-vector coverage — are all expected attack patterns present
  5. Severity calibration — are Critical/High ratings appropriate
  6. Pattern quality — specificity, length, false-positive risk
  7. Compliance mapping — NIST AI RMF, NIST SSDF, SLSA, OWASP ASVS
  8. Gap analysis    — what attack vectors, CWEs, or standards are missing
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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "agent2"

# ── Industry standard reference data ──────────────────────────────────────────

# OWASP Top 10 2025 — rules in this repo use the 2025 numbering (e.g. A05:2025 - Injection)
OWASP_TOP10_2025: dict[str, str] = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",          # 2021 numbering
    "A04": "Insecure Design",
    "A05": "Injection",          # 2025 numbering (confirmed from rule data)
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)",
}

# Maps category text in rule descriptions to canonical CWEs so we can infer
# CWE coverage even when rules lack an explicit cwe: field.
CATEGORY_CWE_INFER: dict[str, list[int]] = {
    "sql injection": [89], "sql": [89],
    "command injection": [78, 77], "command": [78],
    "code injection": [94], "injection": [89, 78, 94],
    "xss": [79], "cross.site scripting": [79], "cross-site scripting": [79],
    "cross site scripting": [79], "unsafe html": [79],
    "ssrf": [918], "server.side request": [918],
    "path traversal": [22], "directory traversal": [22],
    "open redirect": [601],
    "hardcoded credential": [798, 259], "hardcoded": [798],
    "credential": [798, 259], "cloud credential": [798],
    "api key": [798], "secret": [798], "password": [259],
    "jwt": [522, 798], "token": [522],
    "private key": [321], "certificate": [295],
    "weak algorithm": [327, 326], "weak cipher": [327], "weak hash": [328],
    "tls": [326], "ssl": [326], "crypto": [327],
    "missing auth": [306], "authentication": [287],
    "session": [384, 613], "broken auth": [287],
    "broken access": [862, 863], "access control": [862],
    "idor": [639], "privilege": [269],
    "deserialization": [502], "unsafe deserialization": [502],
    "xxe": [611], "xml external": [611],
    "ldap injection": [90],
    "nosql injection": [943],
    "xpath injection": [643],
    "el injection": [917],
    "network exposure": [732], "public access": [732],
    "misconfiguration": [732, 276], "default": [276],
    "logging": [778, 779], "audit": [778],
    "error handling": [209], "exception": [209],
    "supply chain": [1104, 1035], "dependency": [1104],
    "sbom": [1104], "component": [1104],
    "unrestricted upload": [434],
    "csrf": [352],
    "header": [693], "security header": [693],
}

OWASP_LLM_TOP10: dict[str, str] = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain Vulnerabilities",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}

CWE_TOP25: dict[int, str] = {
    79: "Cross-site Scripting", 89: "SQL Injection", 20: "Improper Input Validation",
    78: "OS Command Injection", 22: "Path Traversal", 352: "CSRF",
    434: "Unrestricted Upload", 862: "Missing Authorization", 287: "Improper Authentication",
    502: "Deserialization", 77: "Command Injection", 798: "Hard-coded Credentials",
    918: "SSRF", 306: "Missing Authentication", 269: "Privilege Management",
    94: "Code Injection", 863: "Incorrect Authorization", 276: "Incorrect Default Permissions",
    400: "Uncontrolled Resource Consumption", 190: "Integer Overflow",
    125: "Out-of-bounds Read", 416: "Use After Free", 119: "Buffer Overflow",
    362: "Race Condition", 259: "Hard-coded Password",
}

ASVS_CHAPTERS: dict[str, str] = {
    "V1": "Architecture", "V2": "Authentication", "V3": "Session Management",
    "V4": "Access Control", "V5": "Input Validation", "V6": "Cryptography",
    "V7": "Error Handling and Logging", "V8": "Data Protection",
    "V9": "Communications Security", "V10": "Malicious Code",
    "V11": "Business Logic", "V12": "File and Resource", "V13": "API",
    "V14": "Configuration",
}

NIST_SSDF: dict[str, str] = {
    "PW.1": "Design Software to Meet Security Requirements",
    "PW.2": "Review the Software Design",
    "PW.4": "Reuse Existing, Well-Secured Software",
    "PW.6": "Configure the Compilation and Build Processes",
    "PW.7": "Review and/or Analyze Human-Readable Code",
    "PW.8": "Test Executable Code",
    "RV.1": "Identify and Confirm Vulnerabilities",
    "RV.2": "Assess, Prioritize, and Remediate Vulnerabilities",
    "RV.3": "Analyze Vulnerabilities to Identify Root Causes",
}

VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
VALID_MATCH_STRATEGIES = {
    "regex", "resource_context", "design_review",
    "compliance_review", "checkov_graph_check",
}

# ── Per-skill security profiles ───────────────────────────────────────────────
# Each entry defines what a well-formed skill of this type SHOULD cover.

SKILL_SECURITY_PROFILES: dict[str, dict[str, Any]] = {
    "scan-for-injection": {
        "domain": "SAST", "subcategory": "Injection",
        "owasp_top10": ["A03"],
        "expected_cwes": [89, 78, 94, 77, 943, 90, 611, 917, 643, 74],
        "critical_cwes": [89, 78, 94],
        "asvs_chapters": ["V5"],
        "nist_ssdf": ["PW.7", "RV.1"],
        "attack_keywords": ["sql", "command", "code", "nosql", "ldap", "xxe", "injection", "xpath"],
        "min_rules": 7,
    },
    "scan-for-xss": {
        "domain": "SAST", "subcategory": "XSS",
        "owasp_top10": ["A03"],
        "expected_cwes": [79, 80, 116],
        "critical_cwes": [79],
        "asvs_chapters": ["V5"],
        "nist_ssdf": ["PW.7", "RV.1"],
        "attack_keywords": ["xss", "cross.site", "script", "reflected", "stored", "dom"],
        "min_rules": 5,
    },
    "scan-for-ssrf": {
        "domain": "SAST", "subcategory": "SSRF",
        "owasp_top10": ["A10"],
        "expected_cwes": [918, 441],
        "critical_cwes": [918],
        "asvs_chapters": ["V5", "V9"],
        "nist_ssdf": ["PW.7", "RV.1"],
        "attack_keywords": ["ssrf", "server.side", "request.forgery", "redirect"],
        "min_rules": 5,
    },
    "scan-broken-access-control": {
        "domain": "SAST", "subcategory": "Access Control",
        "owasp_top10": ["A01"],
        "expected_cwes": [862, 863, 639, 284, 285],
        "critical_cwes": [862, 863],
        "asvs_chapters": ["V4"],
        "nist_ssdf": ["PW.2", "RV.1"],
        "attack_keywords": ["access.control", "authorization", "idor", "privilege", "rbac"],
        "min_rules": 8,
    },
    "audit-auth-session-management": {
        "domain": "Compliance", "subcategory": "Authentication",
        "owasp_top10": ["A07"],
        "expected_cwes": [287, 306, 384, 613, 522, 798, 259],
        "critical_cwes": [287, 306],
        "asvs_chapters": ["V2", "V3"],
        "nist_ssdf": ["PW.1", "RV.2"],
        "attack_keywords": ["auth", "session", "credential", "password", "token", "mfa", "jwt"],
        "min_rules": 10,
    },
    "audit-crypto-usage": {
        "domain": "Compliance", "subcategory": "Cryptography",
        "owasp_top10": ["A02"],
        "expected_cwes": [326, 327, 295, 330, 338, 321],
        "critical_cwes": [326, 327],
        "asvs_chapters": ["V6", "V9"],
        "nist_ssdf": ["PW.1"],
        "attack_keywords": ["crypto", "tls", "ssl", "cipher", "hash", "key", "certificate", "weak"],
        "min_rules": 8,
    },
    "audit-logging-monitoring": {
        "domain": "Compliance", "subcategory": "Logging",
        "owasp_top10": ["A09"],
        "expected_cwes": [778, 779, 532, 209],
        "critical_cwes": [],
        "asvs_chapters": ["V7", "V8"],
        "nist_ssdf": ["PW.1"],
        "attack_keywords": ["log", "monitor", "audit", "alert", "trace", "event"],
        "min_rules": 8,
    },
    "audit-asvs-compliance": {
        "domain": "Compliance", "subcategory": "ASVS",
        "owasp_top10": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"],
        "expected_cwes": [79, 89, 287, 326, 862, 306, 78],
        "critical_cwes": [79, 89, 287],
        "asvs_chapters": ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V13", "V14"],
        "nist_ssdf": ["PW.1", "PW.2", "RV.2"],
        "attack_keywords": ["asvs", "requirement", "verification", "compliance", "control"],
        "min_rules": 100,
    },
    "detect-secrets": {
        "domain": "Secrets Detection", "subcategory": "Credential Scanning",
        "owasp_top10": ["A02", "A07"],
        "expected_cwes": [798, 259, 312, 522, 321],
        "critical_cwes": [798, 259],
        "asvs_chapters": ["V8"],
        "nist_ssdf": ["PW.7", "RV.1"],
        "attack_keywords": ["api.key", "password", "token", "secret", "credential", "private.key", "aws", "gcp", "azure"],
        "min_rules": 50,
    },
    "detect-supply-chain-risks": {
        "domain": "SCA", "subcategory": "Supply Chain",
        "owasp_top10": ["A06", "A08"],
        "expected_cwes": [1104, 1035, 494, 829],
        "critical_cwes": [494, 829],
        "asvs_chapters": ["V10", "V14"],
        "nist_ssdf": ["PW.4", "RV.2"],
        "attack_keywords": ["supply.chain", "dependency", "typosquat", "confusion", "provenance", "unsigned"],
        "min_rules": 15,
    },
    "scan-sca-dependencies": {
        "domain": "SCA", "subcategory": "Dependency Scanning",
        "owasp_top10": ["A06"],
        "expected_cwes": [1104, 1035],
        "critical_cwes": [],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.4", "RV.2"],
        "attack_keywords": ["cve", "vulnerable", "dependency", "package", "version", "sbom"],
        "min_rules": 15,
    },
    "scan-iac-security": {
        "domain": "IaC Security", "subcategory": "Infrastructure as Code",
        "owasp_top10": ["A05"],
        "expected_cwes": [250, 732, 276, 269, 311, 319],
        "critical_cwes": [250, 732],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.6", "RV.1"],
        "attack_keywords": ["terraform", "cloudformation", "iac", "misconfiguration", "privilege", "public", "encrypt"],
        "min_rules": 100,
    },
    "scan-kubernetes-manifests": {
        "domain": "Kubernetes Security", "subcategory": "K8s Hardening",
        "owasp_top10": ["A05"],
        "expected_cwes": [250, 732, 276, 269],
        "critical_cwes": [250, 732],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.6", "RV.1"],
        "attack_keywords": ["kubernetes", "pod", "rbac", "privileged", "network.policy", "securitycontext"],
        "min_rules": 50,
    },
    "scan-container-image": {
        "domain": "Container Security", "subcategory": "Docker Hardening",
        "owasp_top10": ["A05"],
        "expected_cwes": [250, 269, 276, 732],
        "critical_cwes": [250],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.6", "RV.1"],
        "attack_keywords": ["docker", "container", "root", "privileged", "image", "layer", "user"],
        "min_rules": 50,
    },
    "scan-api-security": {
        "domain": "API Security", "subcategory": "REST/GraphQL",
        "owasp_top10": ["A01", "A03", "A05", "A07", "A10"],
        "expected_cwes": [862, 287, 918, 89, 79, 307],
        "critical_cwes": [862, 918],
        "asvs_chapters": ["V4", "V13"],
        "nist_ssdf": ["PW.2", "RV.1"],
        "attack_keywords": ["api", "rest", "graphql", "endpoint", "auth", "rate.limit", "debug"],
        "min_rules": 5,
    },
    "scan-static-analysis": {
        "domain": "SAST", "subcategory": "General Static Analysis",
        "owasp_top10": ["A03", "A05"],
        "expected_cwes": [89, 78, 22, 79, 94, 190, 476],
        "critical_cwes": [89, 78],
        "asvs_chapters": ["V5"],
        "nist_ssdf": ["PW.7", "RV.1"],
        "attack_keywords": ["injection", "xss", "traversal", "overflow", "hardcode", "weak"],
        "min_rules": 20,
    },
    "scan-security-headers": {
        "domain": "SAST", "subcategory": "HTTP Security Headers",
        "owasp_top10": ["A05"],
        "expected_cwes": [693, 1021, 116],
        "critical_cwes": [],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.1"],
        "attack_keywords": ["header", "csp", "hsts", "x-frame", "cors", "content.type"],
        "min_rules": 8,
    },
    "scan-exception-handling": {
        "domain": "SAST", "subcategory": "Error Handling",
        "owasp_top10": ["A05"],
        "expected_cwes": [209, 248, 395, 754],
        "critical_cwes": [],
        "asvs_chapters": ["V7"],
        "nist_ssdf": ["PW.7"],
        "attack_keywords": ["exception", "error", "stack.trace", "catch", "finally", "expose"],
        "min_rules": 8,
    },
    "threat-model-system": {
        "domain": "Threat Modeling", "subcategory": "Design Review",
        "owasp_top10": ["A01", "A04", "A06"],
        "expected_cwes": [],
        "critical_cwes": [],
        "asvs_chapters": ["V1"],
        "nist_ssdf": ["PW.1", "PW.2"],
        "attack_keywords": ["threat", "stride", "attack", "trust.boundary", "data.flow", "asset"],
        "min_rules": 10,
    },
    "generate-sbom": {
        "domain": "SBOM", "subcategory": "Bill of Materials",
        "owasp_top10": ["A06", "A08"],
        "expected_cwes": [1104, 1035],
        "critical_cwes": [],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.4"],
        "attack_keywords": ["sbom", "cyclonedx", "spdx", "component", "inventory", "license"],
        "min_rules": 5,
    },
    "generate-dependency-graph": {
        "domain": "SBOM", "subcategory": "Dependency Graph",
        "owasp_top10": ["A06"],
        "expected_cwes": [1104],
        "critical_cwes": [],
        "asvs_chapters": ["V14"],
        "nist_ssdf": ["PW.4"],
        "attack_keywords": ["dependency", "graph", "transitive", "direct", "path"],
        "min_rules": 5,
    },
}

# Default profile for skills not explicitly listed
_DEFAULT_PROFILE: dict[str, Any] = {
    "domain": "General Security",
    "subcategory": "Security Scanning",
    "owasp_top10": [],
    "expected_cwes": [],
    "critical_cwes": [],
    "asvs_chapters": [],
    "nist_ssdf": [],
    "attack_keywords": [],
    "min_rules": 3,
}

# Default for format-scanning skills
_FORMAT_PROFILE: dict[str, Any] = {
    "domain": "Config Security",
    "subcategory": "Configuration File Security",
    "owasp_top10": ["A05"],
    "expected_cwes": [732, 276, 611],
    "critical_cwes": [],
    "asvs_chapters": ["V14"],
    "nist_ssdf": ["PW.1"],
    "attack_keywords": ["inject", "secret", "external", "unsafe", "parse", "expand"],
    "min_rules": 3,
}

for _fmt in ["scan-yaml-security", "scan-json-security", "scan-xml-security",
             "scan-toml-security", "scan-markdown-security"]:
    SKILL_SECURITY_PROFILES[_fmt] = _FORMAT_PROFILE.copy()
    SKILL_SECURITY_PROFILES[_fmt]["subcategory"] = f"{_fmt.split('-')[1].upper()} Security"


# ── Pure validation helpers ────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    text = text.lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text.strip()
    if yaml is None:
        return {}, m.group(2).strip()
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


def _safe_load_yaml(path: Path) -> dict[str, Any]:
    return safe_load_yaml(path)


def _validate_rule_quality(rules: list[dict[str, Any]], rules_data: dict[str, Any]) -> dict[str, Any]:
    """Score every rule against the security skill quality rubric."""
    if not rules:
        return {
            "total_rules": 0, "rules_with_id": 0, "rules_with_severity": 0,
            "rules_with_owasp": 0, "rules_with_cwe": 0, "rules_with_capec": 0,
            "rules_with_remediation": 0, "rules_with_patterns": 0,
            "rules_with_match_strategy": 0, "severity_valid": 0,
            "quality_score": 0.0, "issues": ["No rules found"], "warnings": [],
        }

    issues: list[str] = []
    warnings: list[str] = []
    metrics = {k: 0 for k in [
        "with_id", "with_severity", "with_owasp", "with_cwe", "with_capec",
        "with_remediation", "with_patterns", "with_match_strategy", "severity_valid",
    ]}

    for rule in rules:
        rid = rule.get("id", "")
        if rid:
            metrics["with_id"] += 1
        else:
            issues.append("Rule missing 'id' field")

        sev = rule.get("severity", "")
        if sev:
            metrics["with_severity"] += 1
            if sev in VALID_SEVERITIES:
                metrics["severity_valid"] += 1
            else:
                issues.append(f"{rid}: invalid severity '{sev}'")
        else:
            warnings.append(f"{rid}: missing severity")

        if rule.get("owasp_2025_category"):
            metrics["with_owasp"] += 1
        else:
            warnings.append(f"{rid}: missing OWASP 2025 category mapping")

        if rule.get("cwe"):
            metrics["with_cwe"] += 1
        else:
            warnings.append(f"{rid}: missing CWE mapping")

        if rule.get("capec"):
            metrics["with_capec"] += 1

        if rule.get("remediation"):
            rem = str(rule["remediation"]).strip()
            if len(rem) < 15:
                warnings.append(f"{rid}: remediation too short — should be actionable guidance")
            else:
                metrics["with_remediation"] += 1
        else:
            issues.append(f"{rid}: missing remediation guidance")

        patterns = rule.get("patterns", [])
        strategy = rule.get("match_strategy") or rules_data.get("default_match_strategy", "")
        if strategy in VALID_MATCH_STRATEGIES:
            metrics["with_match_strategy"] += 1
        elif strategy:
            warnings.append(f"{rid}: unknown match_strategy '{strategy}'")
        else:
            warnings.append(f"{rid}: missing match_strategy")

        if isinstance(patterns, list) and patterns:
            metrics["with_patterns"] += 1
            # Pattern quality checks
            for pat in patterns[:3]:
                if len(str(pat)) < 4:
                    warnings.append(f"{rid}: pattern '{pat}' may be too short — high false-positive risk")
        elif strategy not in {"design_review", "compliance_review", "checkov_graph_check"}:
            issues.append(f"{rid}: missing patterns for match_strategy '{strategy}'")

    total = len(rules)
    weights = [
        ("with_id", 1.5), ("with_severity", 1.5), ("with_owasp", 2.0),
        ("with_cwe", 2.0), ("with_remediation", 2.5), ("with_patterns", 1.5),
        ("with_match_strategy", 1.0), ("severity_valid", 1.5), ("with_capec", 0.5),
    ]
    total_weight = sum(w for _, w in weights)
    weighted_score = sum(metrics[k] / total * w for k, w in weights)
    quality_score = round(weighted_score / total_weight * 100, 1) if total else 0.0

    return {
        "total_rules": total,
        "rules_with_id": metrics["with_id"],
        "rules_with_severity": metrics["with_severity"],
        "rules_with_owasp": metrics["with_owasp"],
        "rules_with_cwe": metrics["with_cwe"],
        "rules_with_capec": metrics["with_capec"],
        "rules_with_remediation": metrics["with_remediation"],
        "rules_with_patterns": metrics["with_patterns"],
        "rules_with_match_strategy": metrics["with_match_strategy"],
        "severity_valid_pct": round(metrics["severity_valid"] / max(total, 1) * 100, 1),
        "quality_score": quality_score,
        "issues": issues,
        "warnings": warnings[:20],
    }


def _parse_cwe_field(raw: Any) -> set[int]:
    """Extract CWE IDs from list[int], int, or string formats."""
    if isinstance(raw, list):
        ids: set[int] = set()
        for item in raw:
            if isinstance(item, int):
                ids.add(item)
            else:
                for m in re.finditer(r"\d+", str(item)):
                    ids.add(int(m.group()))
        return ids
    if isinstance(raw, (int, float)):
        return {int(raw)}
    return {int(m.group()) for m in re.finditer(r"\d+", str(raw)) if m.group().isdigit()}


def _infer_cwes_from_category(rules: list[dict[str, Any]]) -> set[int]:
    """Infer CWE IDs from rule category/name/description text when explicit cwe field is absent."""
    inferred: set[int] = set()
    for rule in rules:
        text = " ".join([
            str(rule.get("category", "")),
            str(rule.get("name", "")),
            str(rule.get("description", "")),
        ]).lower()
        for keyword, cwe_ids in CATEGORY_CWE_INFER.items():
            # Use simple substring match (keyword may contain dots used as word-sep)
            search = keyword.replace(".", " ")
            if search in text or keyword in text:
                inferred.update(cwe_ids)
    return inferred


def _analyze_standards_coverage(rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Adaptive standards check — rewards whatever standard is actually present in rules."""
    total = len(rules) or 1
    has_owasp = sum(1 for r in rules if r.get("owasp_2025_category"))
    has_cwe = sum(1 for r in rules if r.get("cwe"))
    has_asvs = sum(1 for r in rules if r.get("asvs_id") or r.get("chapter_id"))
    has_cis = sum(1 for r in rules if r.get("cis_controls") or r.get("recommendation_id"))
    has_capec = sum(1 for r in rules if r.get("capec"))
    any_standard = sum(1 for r in rules if any(r.get(k) for k in
        ["owasp_2025_category", "cwe", "asvs_id", "chapter_id", "cis_controls",
         "recommendation_id", "capec"]))
    return {
        "rules_with_owasp": has_owasp,
        "rules_with_cwe": has_cwe,
        "rules_with_asvs": has_asvs,
        "rules_with_cis": has_cis,
        "rules_with_capec": has_capec,
        "rules_with_any_standard": any_standard,
        "standards_coverage_pct": round(any_standard / total * 100, 1),
        "primary_standard": (
            "asvs" if has_asvs > 0 else
            "cis" if has_cis > 0 else
            "owasp_cwe" if (has_owasp + has_cwe) > 0 else
            "category_only"
        ),
    }


def _analyze_owasp_coverage(
    rules: list[dict[str, Any]], profile: dict[str, Any]
) -> dict[str, Any]:
    """Check which OWASP Top 10 2025 categories are explicitly tagged and which are expected."""
    covered: set[str] = set()
    category_rules: dict[str, list[str]] = {}
    for rule in rules:
        owasp = str(rule.get("owasp_2025_category", ""))
        m = re.match(r"(A\d{2})", owasp)
        if m:
            cat = m.group(1)
            covered.add(cat)
            category_rules.setdefault(cat, []).append(rule.get("id", "?"))

    expected = set(profile.get("owasp_top10", []))
    # Normalise: skills tagged A05:2025 - Injection mean A05; profiles may say A03 (2021)
    # Credit both A03 and A05 for Injection skills
    if "A03" in expected and "A05" in covered:
        covered.add("A03")
    if "A05" in expected and "A03" in covered:
        covered.add("A05")

    missing_expected = expected - covered
    coverage_pct = round(len(expected & covered) / max(len(expected), 1) * 100, 1)
    has_explicit_owasp = any(rule.get("owasp_2025_category") for rule in rules)

    return {
        "covered_categories": {
            c: {"name": OWASP_TOP10_2025.get(c, c), "rule_ids": category_rules.get(c, [])}
            for c in sorted(covered)
        },
        "expected_categories": sorted(expected),
        "missing_expected": sorted(missing_expected),
        "coverage_pct": coverage_pct,
        "owasp_top10_full_coverage": len(missing_expected) == 0,
        "has_explicit_owasp_tags": has_explicit_owasp,
        "gap_note": (
            f"Rules lack explicit owasp_2025_category field — add OWASP tags to all {len(rules)} rules"
            if not has_explicit_owasp and expected else ""
        ),
    }


def _analyze_cwe_coverage(
    rules: list[dict[str, Any]], profile: dict[str, Any]
) -> dict[str, Any]:
    """Identify CWEs covered explicitly (via cwe field) and inferred (via category text)."""
    explicit_cwes: set[int] = set()
    cwe_to_rules: dict[int, list[str]] = {}
    for rule in rules:
        raw = rule.get("cwe")
        if raw is not None:
            for cwe_id in _parse_cwe_field(raw):
                explicit_cwes.add(cwe_id)
                cwe_to_rules.setdefault(cwe_id, []).append(rule.get("id", "?"))

    inferred_cwes = _infer_cwes_from_category(rules) - explicit_cwes
    all_covered = explicit_cwes | inferred_cwes

    expected = set(profile.get("expected_cwes", []))
    critical = set(profile.get("critical_cwes", []))
    missing = expected - all_covered
    missing_critical = critical - all_covered
    top25_covered = all_covered & set(CWE_TOP25.keys())

    explicit_pct = round(len(expected & explicit_cwes) / max(len(expected), 1) * 100, 1)
    inferred_pct = round(len(expected & all_covered) / max(len(expected), 1) * 100, 1)

    return {
        "explicit_cwes": sorted(explicit_cwes),
        "inferred_cwes": sorted(inferred_cwes),
        "covered_cwes": sorted(all_covered),
        "covered_cwe_names": {c: CWE_TOP25.get(c, "Unknown") for c in sorted(all_covered) if c in CWE_TOP25},
        "expected_cwes": sorted(expected),
        "missing_cwes": sorted(missing),
        "missing_critical_cwes": sorted(missing_critical),
        "top25_cwes_covered": sorted(top25_covered),
        "explicit_coverage_pct": explicit_pct,
        "coverage_pct": inferred_pct,
        "critical_coverage": len(missing_critical) == 0,
        "has_explicit_cwe_tags": len(explicit_cwes) > 0,
        "gap_note": (
            f"{len(rules)} rules lack explicit cwe: field — add CWE mappings for traceability"
            if not explicit_cwes and expected else ""
        ),
    }


def _assess_attack_vector_coverage(
    rules: list[dict[str, Any]], body: str, profile: dict[str, Any]
) -> dict[str, Any]:
    """Check whether the expected attack keywords appear in rules or body text."""
    # Build a plain-text index from rule metadata (NOT the raw regex patterns which
    # contain metacharacters) — searching with simple substring is safer and sufficient.
    all_text = (
        " ".join(
            str(rule.get("name", "")) + " " + str(rule.get("description", ""))
            + " " + str(rule.get("category", ""))
            for rule in rules
        )
        + " " + body
    ).lower()

    keywords = profile.get("attack_keywords", [])
    covered: list[str] = []
    missing: list[str] = []
    for kw in keywords:
        # Try several normalised forms of the keyword
        base = kw.lower()
        variants = [base, base.replace(".", ""), base.replace(".", "_"), base.replace(".", "-"), base.replace(".", " ")]
        if any(v in all_text for v in variants):
            covered.append(kw)
        else:
            missing.append(kw)

    pct = round(len(covered) / max(len(keywords), 1) * 100, 1)
    return {
        "covered_vectors": covered,
        "missing_vectors": missing,
        "coverage_pct": pct,
    }


def _assess_severity_distribution(rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyse severity distribution and flag calibration issues."""
    dist: dict[str, int] = {s: 0 for s in ["Critical", "High", "Medium", "Low", "Info"]}
    for rule in rules:
        sev = rule.get("severity", "")
        if sev in dist:
            dist[sev] += 1

    total = sum(dist.values())
    issues: list[str] = []
    if total > 0:
        if dist["Critical"] + dist["High"] == 0:
            issues.append("No Critical or High rules — skill may under-report severity")
        if dist["Critical"] > total * 0.5:
            issues.append(f"{dist['Critical']}/{total} rules are Critical — review severity calibration")
        if dist["Info"] > total * 0.4:
            issues.append(f"{dist['Info']}/{total} rules are Info — consider promoting actionable findings")

    return {"distribution": dist, "total": total, "calibration_issues": issues}


_REGEX_SPECIAL_CHARS = frozenset(r'\^$.|?*+()[]{}')


def _assess_pattern_quality(rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Assess pattern specificity and false-positive risk."""
    total = 0
    too_short = 0
    no_anchors = 0
    single_word = 0
    for rule in rules:
        patterns = rule.get("patterns") or []
        if not isinstance(patterns, list):
            continue
        for pat in patterns:
            total += 1
            s = str(pat)
            if len(s) < 6:
                too_short += 1
            # A pattern with no regex metacharacters is a plain-text match — may be broad
            if not any(c in _REGEX_SPECIAL_CHARS for c in s):
                no_anchors += 1
            # A pure alphabetic word with no structure is the most over-broad case
            if s.isalpha() and len(s) < 10:
                single_word += 1

    if total == 0:
        return {"total_patterns": 0, "fp_risk": "unknown", "issues": []}

    fp_risk = "low"
    issues: list[str] = []
    if too_short / total > 0.2:
        fp_risk = "medium"
        issues.append(f"{too_short}/{total} patterns are very short (<6 chars) — false-positive risk")
    if single_word / total > 0.3:
        fp_risk = "high"
        issues.append(f"{single_word}/{total} patterns are bare single words — overly broad")

    return {
        "total_patterns": total,
        "patterns_too_short": too_short,
        "patterns_no_anchors": no_anchors,
        "patterns_single_word": single_word,
        "fp_risk": fp_risk,
        "issues": issues,
    }


def _map_compliance_frameworks(
    profile: dict[str, Any],
    rule_quality: dict[str, Any],
    owasp: dict[str, Any],
    cwe: dict[str, Any],
) -> dict[str, Any]:
    """Map skill posture to NIST AI RMF, NIST SSDF, OWASP ASVS, and SLSA."""
    total_rules = rule_quality["total_rules"]
    owasp_ok = owasp["coverage_pct"] >= 80 or not profile.get("owasp_top10")
    cwe_ok = cwe["critical_coverage"]
    quality_ok = rule_quality["quality_score"] >= 70

    nist_ai_rmf = {
        "GOVERN": {
            "status": "pass" if quality_ok else "needs_review",
            "evidence": f"Rule quality score: {rule_quality['quality_score']}%",
        },
        "MAP": {
            "status": "pass" if owasp_ok else "needs_review",
            "evidence": f"OWASP coverage: {owasp['coverage_pct']}%",
        },
        "MEASURE": {
            "status": "pass" if total_rules >= profile.get("min_rules", 3) else "needs_review",
            "evidence": f"{total_rules} rules (minimum recommended: {profile.get('min_rules', 3)})",
        },
        "MANAGE": {
            "status": "pass" if cwe_ok else "needs_review",
            "evidence": f"Critical CWEs covered: {cwe['critical_coverage']}",
        },
    }

    nist_ssdf_covered = profile.get("nist_ssdf", [])
    asvs_chapters = profile.get("asvs_chapters", [])

    slsa_level = 1
    if quality_ok and owasp_ok:
        slsa_level = 2
    if quality_ok and owasp_ok and cwe_ok and total_rules >= profile.get("min_rules", 3):
        slsa_level = 3
    if slsa_level == 3 and rule_quality.get("rules_with_capec", 0) / max(total_rules, 1) >= 0.5:
        slsa_level = 4

    compliance_score = round(
        rule_quality["quality_score"] * 0.30
        + owasp["coverage_pct"] * 0.25
        + cwe["coverage_pct"] * 0.25
        + (slsa_level / 4 * 100) * 0.20,
        1,
    )

    return {
        "nist_ai_rmf": nist_ai_rmf,
        "nist_ssdf_practices": nist_ssdf_covered,
        "owasp_asvs_chapters": {ch: ASVS_CHAPTERS[ch] for ch in asvs_chapters if ch in ASVS_CHAPTERS},
        "slsa_level": slsa_level,
        "compliance_score": compliance_score,
        "owasp_llm_top10_applicable": profile["domain"] in {"LLM Security", "General Security"},
    }


def _calculate_security_effectiveness(
    rule_quality: dict[str, Any],
    owasp: dict[str, Any],
    cwe: dict[str, Any],
    attack_vectors: dict[str, Any],
    severity: dict[str, Any],
    pattern: dict[str, Any],
    profile: dict[str, Any],
) -> float:
    """Composite security effectiveness score (0–100)."""
    rule_count_score = min(100.0, rule_quality["total_rules"] / max(profile.get("min_rules", 3) * 1.5, 1) * 100)
    fp_penalty = {"low": 0, "medium": 10, "high": 25, "unknown": 0}.get(pattern["fp_risk"], 0)
    sev_penalty = 10 if severity["calibration_issues"] else 0

    raw = (
        rule_quality["quality_score"] * 0.35       # rule completeness is paramount
        + attack_vectors["coverage_pct"] * 0.25    # domain coverage
        + rule_count_score * 0.15                  # rule count adequacy
        + owasp["coverage_pct"] * 0.13             # OWASP traceability
        + cwe["coverage_pct"] * 0.12               # CWE traceability
        - fp_penalty
        - sev_penalty
    )
    return round(max(0.0, min(100.0, raw)), 1)


def _generate_gaps(
    skill_name: str,
    profile: dict[str, Any],
    rules: list[dict[str, Any]],
    rule_quality: dict[str, Any],
    owasp: dict[str, Any],
    cwe: dict[str, Any],
    attack_vectors: dict[str, Any],
    severity: dict[str, Any],
) -> list[str]:
    """Generate actionable gap findings for this skill."""
    gaps: list[str] = []

    for cat in owasp["missing_expected"]:
        gaps.append(f"OWASP {cat} ({OWASP_TOP10_2025.get(cat, '')}) not covered — expected for {profile['subcategory']}")
    if owasp.get("gap_note"):
        gaps.append(owasp["gap_note"])

    for cwe_id in cwe["missing_critical_cwes"]:
        gaps.append(f"Critical CWE-{cwe_id} ({CWE_TOP25.get(cwe_id, 'Unknown')}) not covered")
    for cwe_id in cwe["missing_cwes"][:5]:
        gaps.append(f"CWE-{cwe_id} ({CWE_TOP25.get(cwe_id, 'Unknown')}) missing from expected coverage")
    if cwe.get("gap_note"):
        gaps.append(cwe["gap_note"])

    for vec in attack_vectors["missing_vectors"][:5]:
        gaps.append(f"Attack vector '{vec}' not addressed by any rule")

    if rule_quality["total_rules"] < profile.get("min_rules", 3):
        gaps.append(
            f"Only {rule_quality['total_rules']} rules — recommend at least "
            f"{profile.get('min_rules', 3)} for comprehensive {profile['subcategory']} coverage"
        )

    for issue in rule_quality["issues"][:5]:
        gaps.append(f"Rule quality: {issue}")

    for issue in severity["calibration_issues"]:
        gaps.append(f"Severity calibration: {issue}")

    return gaps


# ── Agent class ────────────────────────────────────────────────────────────────

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
        skill_dirs = [
            p for p in sorted(self.skills_dir.iterdir())
            if p.is_dir() and not p.name.startswith("_")
        ]
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

        profile = SKILL_SECURITY_PROFILES.get(skill_dir.name, _DEFAULT_PROFILE)

        rule_quality = _validate_rule_quality(rules, rules_data)
        standards = _analyze_standards_coverage(rules)
        owasp = _analyze_owasp_coverage(rules, profile)
        cwe = _analyze_cwe_coverage(rules, profile)
        attack_vectors = _assess_attack_vector_coverage(rules, body, profile)
        severity = _assess_severity_distribution(rules)
        pattern_quality = _assess_pattern_quality(rules)
        compliance = _map_compliance_frameworks(profile, rule_quality, owasp, cwe)
        gaps = _generate_gaps(skill_dir.name, profile, rules, rule_quality, owasp, cwe, attack_vectors, severity)
        score = _calculate_security_effectiveness(rule_quality, owasp, cwe, attack_vectors, severity, pattern_quality, profile)

        overall_risk = (
            "high" if (rule_quality["issues"] and rule_quality["quality_score"] < 50) or cwe["missing_critical_cwes"]
            else "medium" if gaps
            else "low"
        )

        llm = await self.llm.complete_json(
            "You are Agent 2, a security skill validator. Analyze the skill against industry security standards. "
            "Return JSON with keys: security_assessment, compliance_posture, missing_controls, "
            "recommendations, confidence.",
            json.dumps({
                "skill": skill_dir.name,
                "domain": profile["domain"],
                "subcategory": profile["subcategory"],
                "rule_count": len(rules),
                "owasp_coverage_pct": owasp["coverage_pct"],
                "cwe_coverage_pct": cwe["coverage_pct"],
                "quality_score": rule_quality["quality_score"],
                "attack_vector_coverage_pct": attack_vectors["coverage_pct"],
                "gaps_count": len(gaps),
                "gaps_sample": gaps[:3],
                "slsa_level": compliance["slsa_level"],
            }),
            mock_response={
                "security_assessment": (
                    f"{skill_dir.name} covers {profile['domain']} with "
                    f"{len(rules)} rules. OWASP coverage: {owasp['coverage_pct']}%. "
                    f"CWE coverage: {cwe['coverage_pct']}%."
                ),
                "compliance_posture": "good" if score >= 75 else "needs_review",
                "missing_controls": gaps[:3],
                "recommendations": [g for g in gaps[:5]],
                "confidence": 0.82,
            },
        )

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        return {
            "skill": skill_dir.name,
            "generated_at": _now_utc(),
            "confidence": round(min(0.95, 0.70 + score / 1000), 2),
            "security_effectiveness_score": score,
            "overall_risk": overall_risk,
            "domain": profile["domain"],
            "subcategory": profile["subcategory"],
            "rule_quality": rule_quality,
            "standards_coverage": standards,
            "owasp_coverage": owasp,
            "cwe_coverage": cwe,
            "attack_vector_coverage": attack_vectors,
            "severity_distribution": severity,
            "pattern_quality": pattern_quality,
            "compliance": compliance,
            "gaps": gaps,
            "llm": {
                "used_llm": llm.used_llm,
                "model": llm.model,
                "prompt_tokens": llm.prompt_tokens,
                "completion_tokens": llm.completion_tokens,
                "latency_ms": llm.latency_ms,
                "evidence": llm.evidence,
                "response": llm.response,
            },
            "findings": gaps,
            "recommendations": llm.response.get("recommendations", gaps[:5]),
            "evidence": [
                f"Validated {len(rules)} rules in {skill_dir.name} against OWASP/CWE/NIST standards",
                f"OWASP Top 10 2025 coverage: {owasp['coverage_pct']}%",
                f"CWE coverage: {cwe['coverage_pct']}% ({len(cwe['covered_cwes'])} CWEs)",
                f"Rule quality score: {rule_quality['quality_score']}%",
            ],
            "execution_ms": elapsed_ms,
        }

    def _merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        valid = [r for r in results if "error" not in r]
        if not valid:
            return {"agent": "agent2", "error": "No skills analyzed"}

        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for r in valid:
            risk_counts[r.get("overall_risk", "low")] += 1

        avg_score = round(statistics.mean(r["security_effectiveness_score"] for r in valid), 1)
        overall_risk = "high" if risk_counts["high"] > 0 else "medium" if risk_counts["medium"] > 0 else "low"
        all_gaps = [g for r in valid for g in r.get("gaps", [])]

        # OWASP Top 10 2025 aggregate coverage
        owasp_aggregate: dict[str, list[str]] = {}
        for r in valid:
            for cat, data in r["owasp_coverage"]["covered_categories"].items():
                owasp_aggregate.setdefault(cat, []).append(r["skill"])

        total_cwes = len({c for r in valid for c in r["cwe_coverage"]["covered_cwes"]})

        return {
            "agent": "agent2",
            "generated_at": _now_utc(),
            "schema_version": "1.0",
            "skills_analyzed": len(valid),
            "overall_risk": overall_risk,
            "avg_security_effectiveness_score": avg_score,
            "confidence": round(statistics.mean(r["confidence"] for r in valid), 2),
            "skill_results": results,
            "security_report": [
                {
                    "skill": r["skill"],
                    "domain": r["domain"],
                    "overall_risk": r["overall_risk"],
                    "security_effectiveness_score": r["security_effectiveness_score"],
                    "owasp_coverage_pct": r["owasp_coverage"]["coverage_pct"],
                    "cwe_coverage_pct": r["cwe_coverage"]["coverage_pct"],
                    "attack_vector_coverage_pct": r["attack_vector_coverage"]["coverage_pct"],
                    "rule_quality_score": r["rule_quality"]["quality_score"],
                    "gaps_count": len(r["gaps"]),
                }
                for r in valid
            ],
            "compliance_report": [
                {
                    "skill": r["skill"],
                    "governance_valid": r["rule_quality"]["quality_score"] >= 70,
                    "owasp_mapped": r["rule_quality"]["rules_with_owasp"] > 0,
                    "cwe_mapped": r["rule_quality"]["rules_with_cwe"] > 0,
                    "remediation_coverage": round(
                        r["rule_quality"]["rules_with_remediation"] / max(r["rule_quality"]["total_rules"], 1), 2
                    ),
                    "compliance_posture": r["llm"]["response"].get("compliance_posture", "unknown"),
                    "compliance_score": r["compliance"]["compliance_score"],
                    "slsa_level": r["compliance"]["slsa_level"],
                    "owasp_llm_top10_pass": not r["compliance"]["owasp_llm_top10_applicable"],
                    "nist_ai_rmf": {k: v["status"] for k, v in r["compliance"]["nist_ai_rmf"].items()},
                    "asvs_chapters": list(r["compliance"]["owasp_asvs_chapters"].keys()),
                }
                for r in valid
            ],
            "owasp_top10_aggregate": {
                cat: {"name": OWASP_TOP10_2025[cat], "covered_by": skills}
                for cat, skills in owasp_aggregate.items()
            },
            "total_cwes_covered": total_cwes,
            "risk_summary": risk_counts,
            "total_findings": len(all_gaps),
            "all_findings": all_gaps[:100],
            "recommendations": sorted({r for result in valid for r in result.get("recommendations", [])})[:20],
            "downloadable_json": "output/agent2/agent2-report.json",
        }

    def _write(self, report: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "agent2-report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )


async def run_agent2(
    skills_dir: str = "skills",
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
    skills: list[str] | None = None,
    llm: LocalLLMClient | None = None,
) -> dict[str, Any]:
    agent = Agent2(REPO_ROOT / skills_dir, Path(output_dir), llm)
    return await agent.run({"skills": skills or []})
