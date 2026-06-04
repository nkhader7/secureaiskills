from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

from .llm_client import LLMClient
from .agents import run_all
from .report_orchestrator import merge_results, save_report, get_report, list_reports
from .ingest import process_uploaded_zip_bytes

app = FastAPI(title="AI Skill Analysis Framework")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]) 

llm = LLMClient()

class AnalyzeRequest(BaseModel):
    skill_id: str | None = None
    files: Dict[str, str] = {}
    options: Dict[str, Any] = {}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    context = {"skill_id": req.skill_id, "files": req.files, "options": req.options}
    # run agents in parallel
    agent_results = await run_all(llm, context)
    report = merge_results(agent_results, context)
    rid = save_report({"request": req.dict(), "report": report, "agents": agent_results}, req.skill_id)
    return {"report_id": rid, "summary": report}


@app.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    # Only accept zip for now
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip uploads are supported by this endpoint")
    # stream to process_uploaded_zip_bytes
    files = process_uploaded_zip_bytes(file.file)
    context = {"skill_id": file.filename, "files": files}
    agent_results = await run_all(llm, context)
    report = merge_results(agent_results, context)
    rid = save_report({"request": {"skill_id": file.filename}, "report": report, "agents": agent_results}, file.filename)
    return {"report_id": rid, "summary": report}

@app.post("/analyze/structure")
async def analyze_structure(req: AnalyzeRequest):
    context = {"skill_id": req.skill_id, "files": req.files}
    agent1 = (await run_all(llm, context))['agent1']
    return {"agent1": agent1}

@app.post("/analyze/security")
async def analyze_security(req: AnalyzeRequest):
    context = {"skill_id": req.skill_id, "files": req.files}
    agent2 = (await run_all(llm, context))['agent2']
    return {"agent2": agent2}

@app.post("/analyze/testing")
async def analyze_testing(req: AnalyzeRequest):
    context = {"skill_id": req.skill_id, "files": req.files}
    agent3 = (await run_all(llm, context))['agent3']
    return {"agent3": agent3}

@app.post("/analyze/benchmark")
async def analyze_benchmark(req: AnalyzeRequest):
    # placeholder: return simple benchmark metadata
    return {"benchmark": {"estimated_tokens": sum(len(v) for v in req.files.values()) // 4}}

@app.post("/analyze/compliance")
async def analyze_compliance(req: AnalyzeRequest):
    return {"compliance": {"owasp_top10": True, "nistrm": True}}

@app.get("/report/{report_id}")
async def get_report_endpoint(report_id: str):
    r = get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="report not found")
    return r


@app.get("/report/{report_id}/visualizations")
async def get_report_visualizations(report_id: str):
    r = get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="report not found")
    return {"visualizations": r.get('report', {}).get('visualizations', {})}


@app.get("/reports")
async def get_reports_list(limit: int = 100):
    return {"reports": list_reports(limit)}

@app.get("/health")
async def health():
    return {"status": "ok"}
