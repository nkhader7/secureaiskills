# AI Skill Analysis and Governance Framework

This framework runs three agents in parallel over a skill or skill collection:

- Agent 1 understands intent, architecture, lifecycle coverage, dependencies, execution flow, and functional completeness.
- Agent 2 reviews security, privacy, compliance, governance, supply-chain, prompt-injection, and operational risk.
- Agent 3 validates execution, generates tests, converts formats, benchmarks efficiency, creates graph artifacts, and emits CI/CD outputs.

## Run

```bash
python test-projects/ai_skill_framework/orchestrator.py --skills-dir skills --output-dir test-projects/framework-output
python test-projects/ai_skill_framework/ci.py
uvicorn api:app --app-dir test-projects/ai_skill_framework --reload
streamlit run test-projects/ai_skill_framework/streamlit_app.py
```

The framework reads `.env` from the repository root. Agent 3 uses `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL`, and related local LLM settings when available, with deterministic fallback for offline CI.

All three agents receive the same shared `LocalLLMClient` instance from the final orchestrator:

```python
results = await asyncio.gather(
    agent1.run(skill_context),
    agent2.run(skill_context),
    agent3.run(skill_context),
)
```

Each agent returns structured JSON with confidence, evidence, and recommendations. The final orchestrator merges those outputs into executive, security, compliance, coverage, benchmark, test, CI/CD, downloadable JSON, graph, and Streamlit dashboard reports.
