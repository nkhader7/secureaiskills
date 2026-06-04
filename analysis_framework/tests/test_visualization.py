"""Tests for visualization module."""
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from analysis_framework.app.visualization import (
    build_dependency_graph,
    build_execution_graph,
    build_security_coverage_graph,
    build_benchmark_graph,
    build_file_relationship_graph,
    generate_all_visualizations,
)


def test_build_dependency_graph():
    """Test dependency graph generation."""
    files = {
        "main.py": "import requests\nimport json",
        "utils.py": "import os",
    }
    
    graph = build_dependency_graph(files)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) >= 2


def test_build_execution_graph():
    """Test execution graph generation."""
    agents = {"agent1": {}, "agent2": {}, "agent3": {}}
    
    graph = build_execution_graph(agents)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) == 6  # input, 3 agents, orchestrator, output


def test_build_security_coverage_graph():
    """Test security coverage graph generation."""
    findings = [
        {"type": "secret", "severity": "critical"},
        {"type": "sast", "severity": "high"},
        {"type": "sast", "severity": "high"},
        {"type": "dependency", "severity": "medium"},
    ]
    
    graph = build_security_coverage_graph(findings)
    assert "nodes" in graph
    assert "edges" in graph
    assert "summary" in graph
    assert graph["summary"]["total_findings"] == 4


def test_build_benchmark_graph():
    """Test benchmark graph generation."""
    metrics = {
        "token_count": 1200,
        "latency_ms": 2300,
        "complexity_score": 5,
    }
    
    graph = build_benchmark_graph(metrics)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) == 4


def test_build_file_relationship_graph():
    """Test file relationship graph generation."""
    files = {
        "main.py": "print('hello')" * 100,
        "utils.py": "def helper(): pass" * 50,
        "config.yaml": "key: value\n" * 20,
    }
    
    graph = build_file_relationship_graph(files)
    assert "nodes" in graph
    assert "summary" in graph
    assert graph["summary"]["total_files"] == 3


def test_generate_all_visualizations():
    """Test generating all visualizations at once."""
    files = {"test.py": "print('test')", "config.yaml": "key: value"}
    agents = {"agent1": {}, "agent2": {}, "agent3": {}}
    findings = [{"type": "sast", "severity": "high"}]
    metrics = {"token_count": 500, "latency_ms": 1000, "complexity_score": 3}
    
    result = generate_all_visualizations(files, agents, findings, metrics)
    
    assert "dependency_graph" in result
    assert "execution_graph" in result
    assert "security_coverage" in result
    assert "benchmark_graph" in result
    assert "file_relationships" in result
