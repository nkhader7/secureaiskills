"""Shared local LLM client and YAML utilities used by all three agents."""
from __future__ import annotations

import asyncio
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _read_env(root: Path) -> dict[str, str]:
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


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def fallback_rule_parse(text: str, parse_error: str = "") -> dict[str, Any]:
    """Regex-based fallback for YAML files that fail strict parsing (e.g. scan-iac-security)."""
    rules: list[dict[str, Any]] = []
    default_match = (re.search(r"^default_match_strategy:\s*(\S+)", text, re.MULTILINE) or [None, "unspecified"])[1]
    version = (re.search(r"^version:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE) or [None, "1.0"])[1]
    for block in re.split(r"(?=^\s*-\s+id:\s*)", text, flags=re.MULTILINE):
        rid = re.search(r"^\s*-\s+id:\s*(.+?)\s*$", block, re.MULTILINE)
        if not rid:
            continue
        rule: dict[str, Any] = {"id": rid.group(1).strip().strip('"')}
        for key in ["severity", "category", "name", "description", "match_strategy", "remediation"]:
            m = re.search(rf"^\s+{key}:\s*(.+?)\s*$", block, re.MULTILINE)
            if m:
                rule[key] = m.group(1).strip().strip('"')
        pm = re.search(r"^\s+patterns:\s*\n(.*?)(?=^\s+\w|^\s*-\s+id:|\Z)", block, re.MULTILINE | re.DOTALL)
        if pm:
            rule["patterns"] = [
                ln.strip()[2:].strip().strip('"')
                for ln in pm.group(1).splitlines()
                if ln.strip().startswith("- ")
            ]
        rules.append(rule)
    result: dict[str, Any] = {"version": version, "default_match_strategy": default_match, "rules": rules}
    if parse_error:
        result["_parse_warning"] = parse_error
    return result


def safe_load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file, falling back to regex parsing if strict YAML fails."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        import yaml as _yaml
        return _yaml.safe_load(text) or {}
    except Exception as exc:
        return fallback_rule_parse(text, str(exc))


@dataclass
class LLMResult:
    used_llm: bool
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    response: dict[str, Any]
    evidence: list[str] = field(default_factory=list)


class LocalLLMClient:
    def __init__(self, env: dict[str, str]) -> None:
        self.enabled = env.get("LOCAL_LLM_ENABLED", "true").lower() not in {"0", "false", "no"}
        self.base_url = env.get("LOCAL_LLM_BASE_URL", "").rstrip("/")
        self.model = env.get("LOCAL_LLM_MODEL", "local-llm")
        self.api_key = env.get("LOCAL_LLM_API_KEY", "")
        self.timeout = float(env.get("LOCAL_LLM_TIMEOUT_SECONDS", "30"))

    @classmethod
    def from_env_file(cls, root: Path) -> "LocalLLMClient":
        return cls(_read_env(root))

    async def complete_json(self, system: str, user: str, mock_response: dict[str, Any] | None = None) -> LLMResult:
        prompt_tokens = est_tokens(system + user)
        if not self.enabled or not self.base_url:
            return self._mock(prompt_tokens, "LOCAL_LLM_BASE_URL not set.", mock_response)
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        started = time.perf_counter()
        try:
            raw = await asyncio.to_thread(self._post, payload)
            latency_ms = (time.perf_counter() - started) * 1000
            content = raw["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            usage = raw.get("usage") or {}
            return LLMResult(
                used_llm=True,
                model=self.model,
                prompt_tokens=int(usage.get("prompt_tokens", prompt_tokens)),
                completion_tokens=int(usage.get("completion_tokens", est_tokens(content))),
                latency_ms=round(latency_ms, 2),
                response=parsed,
                evidence=["OpenAI-compatible local LLM returned JSON."],
            )
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, OSError) as exc:
            return self._mock(prompt_tokens, f"LLM unavailable; deterministic mock used: {exc}", mock_response)

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "Bearer local",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _mock(self, prompt_tokens: int, reason: str, override: dict[str, Any] | None = None) -> LLMResult:
        response = override or {
            "confidence": 0.75,
            "summary": "Deterministic offline analysis.",
            "findings": [],
            "recommendations": [],
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
