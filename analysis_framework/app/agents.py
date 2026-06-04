import asyncio
from typing import Dict, Any
from .llm_client import LLMClient
from .security_scanner import run_all_scanners

class BaseAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

class Agent1(BaseAgent):
    """Understand the skill: architecture, intent, structure."""
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Summarize skill structure and intent. Files: {list(context.get('files', {}).keys())}"
        resp = await self.llm.call(prompt)
        return {"summary": {"files": list(context.get('files', {}).keys()), "llm": resp}}

class Agent2(BaseAgent):
    """Security, compliance, governance analysis."""
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Analyze security risks. Files: {list(context.get('files', {}).keys())}"
        resp = await self.llm.call(prompt, structured=True)
        files = context.get('files', {}) or {}
        scanner_findings = run_all_scanners(files)
        # Aggregate and add LLM-assessed notes
        return {"findings": scanner_findings, "llm": resp}

class Agent3(BaseAgent):
    """Validate, benchmark, test generation."""
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Generate tests and benchmark hints for files: {list(context.get('files', {}).keys())}"
        resp = await self.llm.call(prompt)
        return {"tests": [{"file": k, "tests": ["basic-sanity"]} for k in context.get('files', {})], "llm": resp}

async def run_all(llm: LLMClient, context: Dict[str, Any]):
    a1 = Agent1(llm)
    a2 = Agent2(llm)
    a3 = Agent3(llm)
    results = await asyncio.gather(a1.run(context), a2.run(context), a3.run(context))
    return {"agent1": results[0], "agent2": results[1], "agent3": results[2]}
