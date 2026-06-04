from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from agent3 import DEFAULT_OUTPUT_DIR, run_agent3


class RunRequest(BaseModel):
    skills_dir: str = "skills"
    output_dir: str = str(DEFAULT_OUTPUT_DIR)
    skills: list[str] = []


app = FastAPI(title="SecureAI Agent 3", version="1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": "agent3"}


@app.post("/agent3/run")
async def run(request: RunRequest) -> dict[str, Any]:
    return await run_agent3(request.skills_dir, request.output_dir, request.skills)


@app.get("/agent3/report")
def report() -> dict[str, Any]:
    path = Path(DEFAULT_OUTPUT_DIR) / "agent3-report.json"
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    import json

    return json.loads(path.read_text(encoding="utf-8"))
