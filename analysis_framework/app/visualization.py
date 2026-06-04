"""Visualization engine for generating graph-ready JSON outputs."""
from typing import Dict, List, Any


def build_dependency_graph(files: Dict[str, str]) -> Dict[str, Any]:
    """Build a dependency graph from files and their references."""
    nodes = []
    edges = []
    
    for idx, (fname, content) in enumerate(files.items()):
        nodes.append({"id": fname, "label": fname, "type": "file", "size": len(content)})
    
    # Simple heuristic: look for import/require statements
    import_patterns = [
        (r"^import\s+(\w+)", "python"),
        (r"^from\s+(\w+)", "python"),
        (r"^require\('([^']+)'\)", "js"),
    ]
    
    for fname, content in files.items():
        import re
        for pattern, lang in import_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                dep = match.group(1)
                if not any(n["id"] == dep for n in nodes):
                    nodes.append({"id": dep, "label": dep, "type": "dependency"})
                edges.append({"source": fname, "target": dep, "type": "imports"})
    
    return {"nodes": nodes, "edges": edges}


def build_execution_graph(agents: Dict[str, Any]) -> Dict[str, Any]:
    """Build an execution graph showing agent dependencies and outputs."""
    nodes = [
        {"id": "input", "label": "Skill Upload", "type": "input"},
        {"id": "agent1", "label": "Agent1: Structure & Intent", "type": "agent"},
        {"id": "agent2", "label": "Agent2: Security & Compliance", "type": "agent"},
        {"id": "agent3", "label": "Agent3: Validation & Benchmarking", "type": "agent"},
        {"id": "orchestrator", "label": "Report Orchestrator", "type": "processor"},
        {"id": "output", "label": "Report Output", "type": "output"},
    ]
    
    edges = [
        {"source": "input", "target": "agent1", "type": "parallel"},
        {"source": "input", "target": "agent2", "type": "parallel"},
        {"source": "input", "target": "agent3", "type": "parallel"},
        {"source": "agent1", "target": "orchestrator", "type": "merge"},
        {"source": "agent2", "target": "orchestrator", "type": "merge"},
        {"source": "agent3", "target": "orchestrator", "type": "merge"},
        {"source": "orchestrator", "target": "output", "type": "generates"},
    ]
    
    return {"nodes": nodes, "edges": edges}


def build_security_coverage_graph(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a graph showing security coverage and severity distribution."""
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    type_counts = {}
    
    for finding in findings:
        sev = finding.get("severity", "low")
        if sev in severity_counts:
            severity_counts[sev] += 1
        ftype = finding.get("type", "unknown")
        type_counts[ftype] = type_counts.get(ftype, 0) + 1
    
    nodes = [
        {"id": "coverage", "label": "Security Coverage", "type": "root"},
    ] + [
        {"id": f"sev-{sev}", "label": f"{sev.title()} ({count})", "type": "severity"}
        for sev, count in severity_counts.items()
    ] + [
        {"id": f"type-{ftype}", "label": f"{ftype.title()} ({count})", "type": "issue_type"}
        for ftype, count in type_counts.items()
    ]
    
    edges = [
        {"source": "coverage", "target": f"sev-{sev}", "type": "categorizes"}
        for sev in severity_counts.keys()
    ] + [
        {"source": "coverage", "target": f"type-{ftype}", "type": "categorizes"}
        for ftype in type_counts.keys()
    ]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "total_findings": len(findings),
            "by_severity": severity_counts,
            "by_type": type_counts,
        }
    }


def build_benchmark_graph(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Build a benchmark comparison graph."""
    nodes = [
        {"id": "benchmark", "label": "Benchmark Results", "type": "root"},
        {"id": "tokens", "label": f"Token Usage: {metrics.get('token_count', 'N/A')}", "type": "metric"},
        {"id": "latency", "label": f"Latency: {metrics.get('latency_ms', 'N/A')}ms", "type": "metric"},
        {"id": "complexity", "label": f"Complexity: {metrics.get('complexity_score', 'N/A')}", "type": "metric"},
    ]
    
    edges = [
        {"source": "benchmark", "target": "tokens", "type": "measures"},
        {"source": "benchmark", "target": "latency", "type": "measures"},
        {"source": "benchmark", "target": "complexity", "type": "measures"},
    ]
    
    return {"nodes": nodes, "edges": edges}


def build_file_relationship_graph(files: Dict[str, str]) -> Dict[str, Any]:
    """Build a graph showing file relationships and sizes."""
    nodes = []
    total_size = 0
    
    for fname, content in files.items():
        size = len(content) if isinstance(content, str) else 0
        total_size += size
        nodes.append({
            "id": fname,
            "label": fname,
            "type": "file",
            "size": size,
            "ext": fname.split('.')[-1] if '.' in fname else 'unknown',
        })
    
    return {
        "nodes": nodes,
        "edges": [],
        "summary": {
            "total_files": len(files),
            "total_bytes": total_size,
        }
    }


def generate_all_visualizations(
    files: Dict[str, str],
    agents: Dict[str, Any],
    findings: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Generate all visualization graphs."""
    return {
        "dependency_graph": build_dependency_graph(files),
        "execution_graph": build_execution_graph(agents),
        "security_coverage": build_security_coverage_graph(findings),
        "benchmark_graph": build_benchmark_graph(metrics),
        "file_relationships": build_file_relationship_graph(files),
    }
