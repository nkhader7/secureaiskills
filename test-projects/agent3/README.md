# Agent 3 Skill Analysis

Agent 3 tests, benchmarks, converts, visualizes, and reports on SecureAI skills.

## Run

```bash
python test-projects/agent3/agent3.py --skills-dir skills --output-dir test-projects/agent3-output
python test-projects/agent3/ci.py
uvicorn fastapi_app:app --app-dir test-projects/agent3 --reload
streamlit run test-projects/agent3/streamlit_app.py
```

## Local LLM Configuration

The runner reads `.env` from the repository root. It supports OpenAI-compatible local/self-hosted endpoints:

```text
LOCAL_LLM_ENABLED=true
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_LLM_MODEL=llama3.1
LOCAL_LLM_API_KEY=
LOCAL_LLM_TIMEOUT_SECONDS=30
```

If the endpoint is unavailable, Agent 3 uses deterministic mock LLM responses so CI can still run offline.
