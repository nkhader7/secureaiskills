from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "test-projects" / "framework-output"
SEVERITIES = ["Critical", "High", "Medium", "Low", "Info"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def read_env(root: Path = REPO_ROOT) -> dict[str, str]:
    env_path = root / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@dataclass
class LLMResult:
    used_llm: bool
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    response: dict[str, Any]
    evidence: list[str]


class LocalLLMClient:
    """Shared OpenAI-compatible local/self-hosted LLM client for all agents."""

    def __init__(self, env: dict[str, str] | None = None) -> None:
        self.env = env if env is not None else read_env()
        self.enabled = self.env.get("LOCAL_LLM_ENABLED", "true").lower() not in {"0", "false", "no"}
        self.base_url = self.env.get("LOCAL_LLM_BASE_URL", "").rstrip("/")
        self.model = self.env.get("LOCAL_LLM_MODEL", "local-llm")
        self.api_key = self.env.get("LOCAL_LLM_API_KEY", "")
        self.timeout = float(self.env.get("LOCAL_LLM_TIMEOUT_SECONDS", "30"))

    async def complete_json(self, system: str, user: str) -> LLMResult:
        prompt_tokens = est_tokens(system + user)
        if not self.enabled or not self.base_url:
            return self._mock(prompt_tokens, "Local LLM disabled or LOCAL_LLM_BASE_URL missing.")

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        started = time.perf_counter()
        try:
            response = await __import__("asyncio").to_thread(self._post, payload)
            latency_ms = (time.perf_counter() - started) * 1000
            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            usage = response.get("usage") or {}
            return LLMResult(
                used_llm=True,
                model=self.model,
                prompt_tokens=int(usage.get("prompt_tokens", prompt_tokens)),
                completion_tokens=int(usage.get("completion_tokens", est_tokens(content))),
                latency_ms=round(latency_ms, 2),
                response=parsed,
                evidence=["Shared local LLM client returned JSON from OpenAI-compatible endpoint."],
            )
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, OSError) as exc:
            return self._mock(prompt_tokens, f"Shared local LLM unavailable; deterministic mock used: {exc}")

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "Bearer local",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _mock(self, prompt_tokens: int, reason: str) -> LLMResult:
        response = {
            "valid": True,
            "analysis_mode": "deterministic-offline",
            "expected_json_contract": ["confidence", "evidence", "recommendations"],
            "confidence": 0.78,
        }
        return LLMResult(
            used_llm=False,
            model="deterministic-mock",
            prompt_tokens=prompt_tokens,
            completion_tokens=est_tokens(json.dumps(response)),
            latency_ms=0.0,
            response=response,
            evidence=[reason],
        )


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text.strip()
    if yaml is None:
        return {}, match.group(2).strip()
    return yaml.safe_load(match.group(1)) or {}, match.group(2).strip()


def fallback_rule_parse(text: str, parse_error: str) -> dict[str, Any]:
    rules: list[dict[str, Any]] = []
    version = (re.search(r"^version:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE) or [None, "1.0"])[1]
    default_match = (re.search(r"^default_match_strategy:\s*(\S+)", text, re.MULTILINE) or [None, "unspecified"])[1]
    for block in re.split(r"(?=^\s*-\s+id:\s*)", text, flags=re.MULTILINE):
        rid = re.search(r"^\s*-\s+id:\s*(.+?)\s*$", block, re.MULTILINE)
        if not rid:
            continue
        rule: dict[str, Any] = {"id": rid.group(1).strip().strip('"')}
        for key in ["severity", "category", "name", "description", "match_strategy", "remediation"]:
            match = re.search(rf"^\s+{key}:\s*(.+?)\s*$", block, re.MULTILINE)
            if match:
                rule[key] = match.group(1).strip().strip('"')
        patterns = re.search(r"^\s+patterns:\s*\n(.*?)(?=^\s+\w|^\s*-\s+id:|\Z)", block, re.MULTILINE | re.DOTALL)
        if patterns:
            rule["patterns"] = [
                line.strip()[2:].strip().strip('"')
                for line in patterns.group(1).splitlines()
                if line.strip().startswith("- ")
            ]
        rules.append(rule)
    return {"version": version, "default_match_strategy": default_match, "rules": rules, "_parse_warning": parse_error}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return yaml.safe_load(text) or {}
    except Exception as exc:
        return fallback_rule_parse(text, str(exc))


def skill_dirs(skills_dir: Path, selected: list[str] | None = None) -> list[Path]:
    wanted = set(selected or [])
    dirs = [p for p in sorted(skills_dir.iterdir()) if p.is_dir() and not p.name.startswith("_")]
    return [p for p in dirs if not wanted or p.name in wanted]


def load_skill(skill_dir: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter(text)
    refs = frontmatter.get("references") or {}
    rules_path = skill_dir / refs.get("rules", "references/rules.yaml")
    template_path = skill_dir / refs.get("report_template", "references/report-template.md")
    rules_data = load_yaml(rules_path)
    template = template_path.read_text(encoding="utf-8", errors="replace") if template_path.exists() else ""
    return {
        "name": skill_dir.name,
        "dir": str(skill_dir),
        "skill_md": str(skill_md),
        "frontmatter": frontmatter,
        "body": body,
        "references": refs,
        "rules_path": str(rules_path),
        "rules_data": rules_data,
        "rules": rules_data.get("rules", []),
        "template_path": str(template_path),
        "template": template,
        "raw_text": text,
    }


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
