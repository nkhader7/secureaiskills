from typing import Dict, Any
import uuid
from .persistence import get_db
from .visualization import generate_all_visualizations

REPORT_STORE: Dict[str, Dict[str, Any]] = {}  # fallback in-memory store

def merge_results(agent_results: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    # Simple merge: collect summaries, findings, and tests
    summary = {}
    findings = []
    tests = []
    context = context or {}
    
    for k, v in agent_results.items():
        if k == 'agent1':
            summary.update(v.get('summary', {}))
        if k == 'agent2':
            findings.extend(v.get('findings', []))
        if k == 'agent3':
            tests.extend(v.get('tests', []))
    
    # Calculate scores
    critical_count = len([f for f in findings if f.get('severity') == 'critical'])
    high_count = len([f for f in findings if f.get('severity') == 'high'])
    security_score = max(0, 100 - (critical_count * 20 + high_count * 10))
    
    # Generate visualizations
    files = context.get('files', {})
    metrics = {
        'token_count': sum(len(str(v)) for v in files.values()) // 4,
        'latency_ms': 0,
        'complexity_score': len(files),
    }
    visualizations = generate_all_visualizations(files, agent_results, findings, metrics)
    
    report = {
        'summary': summary,
        'findings': findings,
        'tests': tests,
        'security_score': security_score,
        'compliance_score': 80,
        'validation_score': 90,
        'overall_score': (security_score + 80 + 90) / 3,
        'pass_fail': 'pass' if security_score >= 70 else 'fail',
        'visualizations': visualizations,
    }
    return report

def save_report(payload: Dict[str, Any], skill_id: str = None) -> str:
    rid = str(uuid.uuid4())
    # Try to save to DB, fallback to in-memory
    try:
        db = get_db()
        db.save_report(rid, skill_id or 'unknown', payload.get('report', payload))
    except Exception as e:
        print(f"Warning: could not save to DB: {e}, using in-memory store")
    REPORT_STORE[rid] = payload
    return rid

def get_report(rid: str) -> Dict[str, Any]:
    # Try DB first, fallback to in-memory
    try:
        db = get_db()
        report = db.get_report(rid)
        if report:
            return report
    except Exception:
        pass
    return REPORT_STORE.get(rid, {})


def list_reports(limit: int = 100) -> list:
    """List recent reports from DB."""
    try:
        db = get_db()
        return db.list_reports(limit)
    except Exception:
        return []
