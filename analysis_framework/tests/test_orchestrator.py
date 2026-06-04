import asyncio
from analysis_framework.app.llm_client import LLMClient
from analysis_framework.app.agents import run_all

async def test_run_all():
    llm = LLMClient()
    ctx = {"files": {"a.md": "no secrets here", "b.py": "api_key = 'SECRET'"}}
    res = await run_all(llm, ctx)
    assert 'agent1' in res and 'agent2' in res and 'agent3' in res

if __name__ == '__main__':
    asyncio.run(test_run_all())
