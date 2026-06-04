import os
import asyncio
from typing import Any, Dict

import httpx

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000")
LLM_MODEL = os.getenv("LLM_MODEL", "local")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_MOCK_MODE = os.getenv("LLM_MOCK_MODE", "true").lower() in ("1","true","yes")

class LLMClient:
    def __init__(self, base_url: str = LLM_BASE_URL, model: str = LLM_MODEL, timeout: int = LLM_TIMEOUT):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        await self._client.aclose()

    async def call(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        if LLM_MOCK_MODE:
            # Deterministic mock response for testing
            await asyncio.sleep(0.05)
            return {"model": self.model, "mock": True, "prompt_len": len(prompt), "text": "MOCK_RESPONSE"}

        payload = {"model": self.model, "prompt": prompt}
        url = f"{self.base_url}/v1/generate"

        for attempt in range(LLM_MAX_RETRIES):
            try:
                resp = await self._client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt + 1 >= LLM_MAX_RETRIES:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))
