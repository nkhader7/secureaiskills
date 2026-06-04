import asyncio
import sys
import os

# Ensure project root is on sys.path for test import resolution
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from analysis_framework.app.llm_client import LLMClient
from analysis_framework.app.agents import run_all

async def _run_all_case():
    llm = LLMClient()
    ctx = {"files": {"a.md": "no secrets here", "b.py": "api_key = 'SECRET'"}}
    res = await run_all(llm, ctx)
    assert 'agent1' in res and 'agent2' in res and 'agent3' in res

def test_run_all():
    asyncio.run(_run_all_case())

if __name__ == '__main__':
    asyncio.run(_run_all_case())
