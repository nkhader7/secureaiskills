"""FastAPI service exposing upload ingestion, all three agents, and the orchestrator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile

from agents.agent1 import run_agent1
from agents.agent2 import run_agent2
from agents.agent3 import run_agent3
from agents.ingest import ingest_bytes, ingest_path
from agents.orchestrator import DEFAULT_OUTPUT_DIR, run_all
from agents.schemas import AnalyzeRequest, Thresholds, UploadAnalyzeResponse, apply_thresholds

app = FastAPI(
    title="SecureAI Skills - 3-Agent Framework",
    version="2.1",
    description="Agent 1: Intelligence | Agent 2: Security & Governance | Agent 3: Validate & Benchmark",
)


def _read_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report not found at {path}. Run the analysis first.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "agents": ["agent1", "agent2", "agent3"],
        "endpoints": [
            "/analyze",
            "/analyze/upload",
            "/analyze/path",
            "/analyze/structure",
            "/analyze/security",
            "/analyze/testing",
            "/analyze/benchmark",
            "/analyze/compliance",
            "/report/{report_id}",
        ],
    }


@app.get("/skills")
def list_skills() -> dict[str, Any]:
    skills_dir = Path("skills")
    if not skills_dir.exists():
        return {"skills": [], "count": 0}
    names = sorted(d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith("_"))
    return {"skills": names, "count": len(names)}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    report = await run_all(request.skills_dir, request.skills or None)
    report["threshold_gate"] = apply_thresholds(report, request.thresholds)
    return report


@app.post("/analyze/upload", response_model=UploadAnalyzeResponse)
async def analyze_upload(file: UploadFile = File(...), thresholds: Thresholds = Thresholds()) -> dict[str, Any]:
    try:
        data = await file.read()
        ingested = ingest_bytes(file.filename or "uploaded-skill", data)
        report_dir = DEFAULT_OUTPUT_DIR / "uploads" / ingested.upload_id / "reports"
        report = await run_all(str(ingested.skills_dir), None, str(report_dir))
        report["threshold_gate"] = apply_thresholds(report, thresholds)
        return {
            "upload_id": ingested.upload_id,
            "skills_dir": str(ingested.skills_dir),
            "files": ingested.files,
            "warnings": ingested.warnings,
            "report": report,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/analyze/path")
async def analyze_path(path: str, thresholds: Thresholds = Thresholds()) -> dict[str, Any]:
    try:
        ingested = ingest_path(Path(path))
        report_dir = DEFAULT_OUTPUT_DIR / "uploads" / ingested.upload_id / "reports"
        report = await run_all(str(ingested.skills_dir), None, str(report_dir))
        report["threshold_gate"] = apply_thresholds(report, thresholds)
        return {
            "upload_id": ingested.upload_id,
            "skills_dir": str(ingested.skills_dir),
            "files": ingested.files,
            "warnings": ingested.warnings,
            "report": report,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/analyze/structure")
async def analyze_structure(request: AnalyzeRequest) -> dict[str, Any]:
    return await run_agent1(request.skills_dir, skills=request.skills or None)


@app.post("/analyze/security")
async def analyze_security(request: AnalyzeRequest) -> dict[str, Any]:
    return await run_agent2(request.skills_dir, skills=request.skills or None)


@app.post("/analyze/testing")
async def analyze_testing(request: AnalyzeRequest) -> dict[str, Any]:
    report = await run_agent3(request.skills_dir, skills=request.skills or None)
    return {"test_report": report.get("test_report", []), "ci_cd_report": report.get("ci_cd_report", []), "agent3": report}


@app.post("/analyze/benchmark")
async def analyze_benchmark(request: AnalyzeRequest) -> dict[str, Any]:
    report = await run_agent3(request.skills_dir, skills=request.skills or None)
    return {"benchmark_report": report.get("benchmark_report", []), "graph_artifacts": report.get("graph_artifacts", {})}


@app.post("/analyze/compliance")
async def analyze_compliance(request: AnalyzeRequest) -> dict[str, Any]:
    report = await run_agent2(request.skills_dir, skills=request.skills or None)
    return {"compliance_report": report.get("compliance_report", []), "security_report": report.get("security_report", [])}


@app.post("/run")
async def run_legacy(request: AnalyzeRequest) -> dict[str, Any]:
    return await analyze(request)


@app.post("/agent1/run")
async def run_agent1_endpoint(request: AnalyzeRequest) -> dict[str, Any]:
    return await analyze_structure(request)


@app.post("/agent2/run")
async def run_agent2_endpoint(request: AnalyzeRequest) -> dict[str, Any]:
    return await analyze_security(request)


@app.post("/agent3/run")
async def run_agent3_endpoint(request: AnalyzeRequest) -> dict[str, Any]:
    return await run_agent3(request.skills_dir, skills=request.skills or None)


@app.get("/report")
def full_report() -> dict[str, Any]:
    return _read_report(DEFAULT_OUTPUT_DIR / "full-report.json")


@app.get("/report/{report_id}")
def report_by_id(report_id: str) -> dict[str, Any]:
    mapping = {
        "full": DEFAULT_OUTPUT_DIR / "full-report.json",
        "executive": DEFAULT_OUTPUT_DIR / "full-report.json",
        "structure": DEFAULT_OUTPUT_DIR / "agent1" / "agent1-report.json",
        "agent1": DEFAULT_OUTPUT_DIR / "agent1" / "agent1-report.json",
        "security": DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json",
        "compliance": DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json",
        "agent2": DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json",
        "testing": DEFAULT_OUTPUT_DIR / "agent3" / "agent3-report.json",
        "benchmark": DEFAULT_OUTPUT_DIR / "agent3" / "benchmark-report.json",
        "agent3": DEFAULT_OUTPUT_DIR / "agent3" / "agent3-report.json",
    }
    if report_id not in mapping:
        raise HTTPException(status_code=404, detail=f"Unknown report id: {report_id}")
    return _read_report(mapping[report_id])


@app.get("/report/agent1")
def agent1_report() -> dict[str, Any]:
    return _read_report(DEFAULT_OUTPUT_DIR / "agent1" / "agent1-report.json")


@app.get("/report/agent2")
def agent2_report() -> dict[str, Any]:
    return _read_report(DEFAULT_OUTPUT_DIR / "agent2" / "agent2-report.json")


@app.get("/report/agent3")
def agent3_report() -> dict[str, Any]:
    return _read_report(DEFAULT_OUTPUT_DIR / "agent3" / "agent3-report.json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
