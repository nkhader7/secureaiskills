# AI Skill Analysis Framework

A production-grade, modular, multi-agent framework for comprehensive AI skill analysis. Analyze, secure, validate, benchmark, and govern AI skills before deployment.

## Features

- **🔍 Three-Agent Architecture**
  - Agent1: Skill structure, intent, and functional analysis
  - Agent2: Security, compliance, and governance analysis  
  - Agent3: Validation, testing, and benchmarking
  - Agents run in parallel with concurrent LLM calls

- **🔐 Security Analysis**
  - Secret detection (API keys, credentials, private keys)
  - SAST pattern detection (eval, exec, os.system, subprocess shell)
  - Prompt injection detection
  - Unpinned dependency detection
  - OWASP, NIST, CIS, CWE mapping

- **📦 Multi-Format Support**
  - ZIP archives with safe extraction (path traversal protection)
  - Individual files (Python, YAML, TOML, JSON, Markdown, etc.)
  - Repositories and multi-file collections
  - Binary file handling

- **✅ Compliance & Standards Mapping**
  - OWASP Top 10 for LLM Applications
  - NIST AI Risk Management Framework
  - CIS Controls
  - OWASP ASVS
  - CWE references
  - SLSA (Supply chain Levels for Software Artifacts)

- **📊 Visualization & Dashboards**
  - Dependency graphs
  - Execution flow graphs
  - Security coverage metrics
  - File relationship maps
  - Benchmark comparisons

- **💾 Report Persistence**
  - SQLite database for long-term storage
  - Full report retrieval and listing
  - Timestamped archives

- **🚀 API-First Architecture**
  - RESTful FastAPI endpoints
  - JSON input/output
  - CI/CD integration ready
  - OpenAPI documentation (auto-generated)

- **🧪 Comprehensive Testing**
  - Unit tests for scanners, ingest, persistence, visualization
  - Integration tests for orchestrator
  - Mock LLM mode for offline testing
  - GitHub Actions CI workflow

## Quick Start

### 1. Set up virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r analysis_framework/requirements.txt
```

### 2. Configure environment

```powershell
Copy-Item analysis_framework\.env.example analysis_framework\.env
```

Edit `.env` and set:
- `LLM_BASE_URL` — your local LLM endpoint (default: `http://localhost:8000`)
- `LLM_MODEL` — model name (default: `local`)
- `LLM_MOCK_MODE` — set to `false` for real LLM, `true` for testing (default: `true`)
- `LLM_CLIENT_ID` / `LLM_CLIENT_SECRET` — optional authentication

### 3. Run FastAPI backend

```bash
cd analysis_framework
uvicorn app.main:app --reload --host 127.0.0.1 --port 9000
```

API docs available at: http://127.0.0.1:9000/docs

### 4. Run Streamlit UI (optional, in a new terminal)

```bash
streamlit run analysis_framework/ui/streamlit_app.py
```

UI available at: http://localhost:8501

### 5. Run tests

```bash
pytest -q
```

## API Endpoints

### Upload and Analyze

```bash
POST /analyze/upload
```

Upload a ZIP file containing a skill:

```bash
curl -X POST http://localhost:9000/analyze/upload \n  -F "file=@skill.zip"
```

Response:
```json
{
  "report_id": "uuid-string",
  "summary": {
    "security_score": 85,
    "compliance_score": 90,
    "validation_score": 80,
    "overall_score": 85,
    "pass_fail": "pass",
    "findings": [...],
    "visualizations": {...}
  }
}
```

### Direct Analysis (JSON)

```bash
POST /analyze
```

Send files as JSON:

```json
{
  "skill_id": "my-skill",
  "files": {
    "main.py": "print('hello')",
    "config.yaml": "key: value"
  }
}
```

### Get Report

```bash
GET /report/{report_id}
```

Retrieve a stored report:

```bash
curl http://localhost:9000/report/uuid-string
```

### List Reports

```bash
GET /reports?limit=100
```

List recent reports:

```bash
curl http://localhost:9000/reports?limit=50
```

### Get Visualizations

```bash
GET /report/{report_id}/visualizations
```

Retrieve graphs and charts for a report.

### Health Check

```bash
GET /health
```

## Architecture

### Directory Structure

```
analysis_framework/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── llm_client.py           # Local LLM client with auth/retries
│   ├── agents.py               # Three-agent definitions
│   ├── report_orchestrator.py  # Report merging and persistence
│   ├── security_scanner.py     # Security scanners (secrets, SAST, etc.)
│   ├── ingest.py               # Safe ZIP extraction and file indexing
│   ├── persistence.py          # SQLite ORM for reports
│   ├── visualization.py        # Graph and visualization generation
│   └── schemas.py              # Pydantic models
├── ui/
│   └── streamlit_app.py        # Streamlit multi-page UI
├── tests/
│   ├── test_orchestrator.py
│   ├── test_security_scanner.py
│   ├── test_ingest.py
│   ├── test_persistence.py
│   └── test_visualization.py
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

### Agent Flow

```
Skill Upload
    ↓
[Safe ZIP Extraction]
    ↓
[File Indexing]
    ↓
    ├─→ Agent1 (Structure)    ←┐
    ├─→ Agent2 (Security)     ├─→ Report Orchestrator
    └─→ Agent3 (Validation)   ←┘
            ↓
    [Score Calculation]
    [Visualization Generation]
    [SQLite Persistence]
            ↓
    Report JSON + Graphs
```

## Configuration

### Environment Variables (.env)

```env
# LLM Configuration
LLM_BASE_URL=http://localhost:8000
LLM_MODEL=local-model
LLM_TIMEOUT=60
LLM_MAX_RETRIES=3
LLM_MOCK_MODE=true
LLM_CLIENT_ID=
LLM_CLIENT_SECRET=

# Application
APP_HOST=127.0.0.1
APP_PORT=9000

# Persistence
SKILL_ANALYSIS_DB=analysis_framework/reports.db
```

### LLM Integration

#### Mock Mode (Testing)
Set `LLM_MOCK_MODE=true` to use deterministic mock responses without calling a real LLM.

#### Real LLM (Production)
Set `LLM_MOCK_MODE=false` and point `LLM_BASE_URL` to your self-hosted model.

Supported endpoints:
- OpenAI-compatible: `POST /v1/generate`
- Expects JSON response with `text` or model output

## Extending the Framework

### Adding a New Scanner

1. Add detection function to `security_scanner.py`:

```python
def detect_custom_issue(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    for name, content in files.items():
        if "bad_pattern" in content:
            findings.append({
                "file": name,
                "type": "custom",
                "severity": "high",
                "owasp_llm": "OWASP LLM-XX: ...",
            })
    return findings
```

2. Call it in `run_all_scanners()`:

```python
findings.extend(detect_custom_issue(files))
```

3. Add tests in `tests/test_security_scanner.py`

### Adding a New Visualization

1. Add function to `visualization.py`:

```python
def build_custom_graph(data: Dict) -> Dict[str, Any]:
    return {"nodes": [...], "edges": [...]}
```

2. Call it in `generate_all_visualizations()`

### Customizing Agents

Edit `agents.py` to implement your own logic:

```python
class Agent1(BaseAgent):
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your custom logic here
        pass
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Security Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - run: pip install -r analysis_framework/requirements.txt
      - run: pytest -q
      - run: |
          python -c "
          import asyncio
          from analysis_framework.app.main import app
          from analysis_framework.app.llm_client import LLMClient
          from analysis_framework.app.agents import run_all
          from analysis_framework.app.report_orchestrator import merge_results
          
          # Run analysis on uploaded files
          # Then check thresholds
          if report['security_score'] < 70:
            exit(1)
          "
```

## Troubleshooting

### Tests fail with "No module named 'analysis_framework'"

Ensure project root is in Python path:

```bash
set PYTHONPATH=%cd%
pytest -q
```

### SQLite database already in use

Delete the database file to start fresh:

```bash
rm analysis_framework/reports.db
```

### LLM client timeout

Increase `LLM_TIMEOUT` in `.env` or disable mock mode to test locally.

## Security Notes

- **ZIP Extraction**: All ZIP files are extracted with path traversal protection
- **File Size Limits**: Configurable per-file limits (default 50MB) prevent zip bombs
- **Secret Detection**: Uses regex patterns; for production, integrate industry tools (GitGuardian, TruffleHog, etc.)
- **LLM Auth**: Supports optional client ID/secret for self-hosted models
- **Database**: SQLite is suitable for small deployments; migrate to PostgreSQL for production

## Performance

- **Parallel Agents**: All three agents run concurrently
- **Async LLM**: Non-blocking HTTP calls with retries and timeouts
- **Mock Mode**: ~0.05s per agent call for testing
- **Real LLM**: Depends on model latency (typically 2-5s per analysis)
- **Database**: SQLite queries complete in <50ms

## Future Enhancements

- [ ] Streaming LLM responses for large skills
- [ ] Additional scanners (container security, Kubernetes manifests)
- [ ] Advanced compliance frameworks (SOC2, ISO27001)
- [ ] Machine learning for anomaly detection
- [ ] Web-based report editor and annotation tools
- [ ] Integration with JIRA, GitHub Issues for auto-remediation
- [ ] Kubernetes operator for distributed analysis
- [ ] GraphQL API in addition to REST

## License

See LICENSE file in repository root.

## Support

For issues, feature requests, or contributions, please open an issue or PR in the repository.

---

**Version**: 1.0.0 | **Last Updated**: June 2026
