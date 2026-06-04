import os
import asyncio
import json
from typing import Any, Dict, AsyncIterator, List, Optional

import httpx

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000")
LLM_MODEL = os.getenv("LLM_MODEL", "local")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_MOCK_MODE = os.getenv("LLM_MOCK_MODE", "true").lower() in ("1", "true", "yes")
LLM_CLIENT_ID = os.getenv("LLM_CLIENT_ID")
LLM_CLIENT_SECRET = os.getenv("LLM_CLIENT_SECRET")


class LLMClient:
    def __init__(self, base_url: str = LLM_BASE_URL, model: str = LLM_MODEL, timeout: int = LLM_TIMEOUT):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        await self._client.aclose()

    def _auth_headers(self) -> Dict[str, str]:
        headers = {}
        if LLM_CLIENT_ID and LLM_CLIENT_SECRET:
            headers["X-Client-Id"] = LLM_CLIENT_ID
            headers["X-Client-Secret"] = LLM_CLIENT_SECRET
        return headers

    async def call(self, prompt: str, stream: bool = False, structured: bool = False) -> Any:
        """Call the local LLM. Returns structured JSON when available.

        - `stream`: placeholder for streaming mode (returns list of chunks in mock)
        - `structured`: try to parse JSON from model output
        """
        if LLM_MOCK_MODE:
            # Deterministic mock response for testing
            await asyncio.sleep(0.02)
            text = f"MOCK_RESPONSE for prompt_len={len(prompt)}"
            if stream:
                return [text[i:i+40] for i in range(0, len(text), 40)]
            if structured:
                return {"model": self.model, "mock": True, "parsed": {"summary": "mocked"}, "text": text}
            return {"model": self.model, "mock": True, "text": text}

        payload = {"model": self.model, "prompt": prompt}
        url = f"{self.base_url}/v1/generate"
        headers = self._auth_headers()

        last_exc: Optional[Exception] = None
        for attempt in range(max(1, LLM_MAX_RETRIES)):
            try:
                resp = await self._client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                text = resp.text
                if structured:
                    try:
                        return resp.json()
                    except Exception:
                        # attempt to parse JSON inside text
                        try:
                            return json.loads(text)
                        except Exception:
                            return {"text": text}
                if stream:
                    # Non-blocking placeholder: split into chunks
                    return [text[i:i+2048] for i in range(0, len(text), 2048)]
                return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"text": text}
            except Exception as e:
                last_exc = e
                await asyncio.sleep(0.5 * (attempt + 1))
        raise last_exc

