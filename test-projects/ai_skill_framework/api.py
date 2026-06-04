from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from common import DEFAULT_OUTPUT_DIR
from orchestrator import run_framework


class RunRequest(BaseModel):
    skills_dir: str = "skills"
    output_dir: str = str(DEFAULT_OUTPUT_DIR)
    skills: list[str] = []


app = FastAPI(title="AI Skill Analysis and Governance Framework", version="1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "framework": "ai-skill-analysis-governance-framework"}


@app.post("/framework/run")
async def run(request: RunRequest) -> dict[str, Any]:
    return await run_framework(request.skills_dir, request.output_dir, request.skills)


@app.get("/framework/report")
def report() -> dict[str, Any]:
    path = Path(DEFAULT_OUTPUT_DIR) / "final-orchestrator-report.json"
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))
