Analysis Framework — 3-Agent AI Skill Analysis

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure your LLM.

3. Run the FastAPI app:

```bash
uvicorn analysis_framework.app.main:app --reload --host 127.0.0.1 --port 9000
```

4. Run the Streamlit UI (optional):

```bash
streamlit run analysis_framework/ui/streamlit_app.py
```

What is included

- `analysis_framework/app` — FastAPI app, LLM client, agents, orchestrator, schemas
- `analysis_framework/ui` — Streamlit UI that interacts with the API
- `.env.example` — sample environment variables
- `requirements.txt` — pinned dependencies for local testing
- `analysis_framework/tests` — basic unit tests

Design notes

- The LLM client supports mock mode for offline testing.
- Agents are asynchronous and run in parallel; a report orchestrator merges results.
- This scaffold is intentionally minimal; extend agents and scanners per your rules and skill formats.
