from typing import Dict, Any
import uuid

REPORT_STORE: Dict[str, Dict[str, Any]] = {}

def merge_results(agent_results: Dict[str, Any]) -> Dict[str, Any]:
    # Simple merge: collect summaries, findings, and tests
    summary = {}
    findings = []
    tests = []
    for k, v in agent_results.items():
        if k == 'agent1':
            summary.update(v.get('summary', {}))
        if k == 'agent2':
            findings.extend(v.get('findings', []))
        if k == 'agent3':
            tests.extend(v.get('tests', []))
    score = 100 - min(50, len(findings) * 10)
    report = {
        'summary': summary,
        'findings': findings,
        'tests': tests,
        'security_score': score,
        'compliance_score': 80,
        'validation_score': 90,
    }
    return report

def save_report(payload: Dict[str, Any]) -> str:
    rid = str(uuid.uuid4())
    REPORT_STORE[rid] = payload
    return rid

def get_report(rid: str) -> Dict[str, Any]:
    return REPORT_STORE.get(rid, {})
