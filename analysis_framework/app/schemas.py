from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AnalyzeRequest(BaseModel):
    skill_id: Optional[str]
    files: Optional[Dict[str, str]] = {}
    options: Optional[Dict[str, Any]] = {}

class AgentResult(BaseModel):
    agent: str
    result: Dict[str, Any]

class AnalyzeResponse(BaseModel):
    summary: Dict[str, Any]
    agent_results: List[AgentResult]

class Report(BaseModel):
    id: str
    payload: Dict[str, Any]
