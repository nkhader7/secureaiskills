"""Shared local LLM client and YAML utilities used by all three agents."""
from __future__ import annotations

import asyncio
import base64
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
        self.base_url = (env.get("LOCAL_LLM_BASE_URL") or env.get("LLM_BASE_URL") or "").rstrip("/")
        self.model = env.get("LOCAL_LLM_MODEL") or env.get("LLM_MODEL") or "local-llm"
        self.api_key = env.get("LOCAL_LLM_API_KEY") or env.get("LLM_API_KEY", "")
        self.client_id = env.get("LOCAL_LLM_CLIENT_ID") or env.get("LLM_CLIENT_ID", "")
        self.client_secret = env.get("LOCAL_LLM_CLIENT_SECRET") or env.get("LLM_CLIENT_SECRET", "")
        self.timeout = float(env.get("LOCAL_LLM_TIMEOUT_SECONDS") or env.get("LLM_TIMEOUT") or "30")
        self.max_retries = int(env.get("LOCAL_LLM_MAX_RETRIES") or env.get("LLM_MAX_RETRIES") or "1")

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
        last_exc: Exception | None = None
        for attempt in range(1, max(self.max_retries, 1) + 1):
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
                    evidence=[f"OpenAI-compatible local LLM returned JSON on attempt {attempt}."],
                )
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, OSError) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    await asyncio.sleep(min(0.25 * attempt, 1.0))
        return self._mock(prompt_tokens, f"LLM unavailable; deterministic mock used: {last_exc}", mock_response)

    async def stream_json(self, system: str, user: str, mock_response: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Streaming-compatible facade for local test mode.

        Local gateways vary widely in streaming protocol. The framework exposes a
        stable async method now and returns a single structured event when the
        endpoint is non-streaming or mock mode is active.
        """
        result = await self.complete_json(system, user, mock_response)
        return [{"event": "complete", "data": result.response, "model": result.model, "used_llm": result.used_llm}]

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.client_id or self.client_secret:
            token = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("ascii")
            headers["Authorization"] = f"Basic {token}"
        else:
            headers["Authorization"] = "Bearer local"
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers=headers,
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
