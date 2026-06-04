"""Tests for agents — deterministic offline mode (no LLM required)."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"
REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("skill_name", ["scan-for-injection", "detect-secrets", "threat-model-system"])
def test_agent1_single_skill(skill_name: str, tmp_path: Path) -> None:
    if not (SKILLS_DIR / skill_name).exists():
        pytest.skip("skills directory not available")
    from agents.agent1 import Agent1

    agent = Agent1(skills_dir=SKILLS_DIR, output_dir=tmp_path / "a1")
    result = asyncio.run(agent.run({"skills": [skill_name]}))
    assert result["skills_analyzed"] == 1
    cr = result.get("coverage_report", [])
    assert len(cr) == 1
    assert cr[0]["skill"] == skill_name


@pytest.mark.parametrize("skill_name", ["scan-for-injection", "scan-container-image"])
def test_agent2_single_skill(skill_name: str, tmp_path: Path) -> None:
    if not (SKILLS_DIR / skill_name).exists():
        pytest.skip("skills directory not available")
    from agents.agent2 import Agent2

    agent = Agent2(skills_dir=SKILLS_DIR, output_dir=tmp_path / "a2")
    result = asyncio.run(agent.run({"skills": [skill_name]}))
    assert result["skills_analyzed"] == 1
    sr = result.get("security_report", [])
    assert len(sr) == 1
    assert sr[0]["overall_risk"] in {"low", "medium", "high"}


def test_agent2_compliance_fields(tmp_path: Path) -> None:
    skill_name = "scan-for-injection"
    if not (SKILLS_DIR / skill_name).exists():
        pytest.skip("skills directory not available")
    from agents.agent2 import Agent2

    agent = Agent2(skills_dir=SKILLS_DIR, output_dir=tmp_path / "a2")
    result = asyncio.run(agent.run({"skills": [skill_name]}))
    cr = result.get("compliance_report", [])
    assert len(cr) == 1
    assert "compliance_score" in cr[0]
    assert "slsa_level" in cr[0]
    assert "owasp_llm_top10_pass" in cr[0]
    assert "nist_ai_rmf" in cr[0]


def test_agent3_graphs_complete(tmp_path: Path) -> None:
    skill_name = "scan-for-injection"
    if not (SKILLS_DIR / skill_name).exists():
        pytest.skip("skills directory not available")
    from agents.agent3 import Agent3

    agent = Agent3(skills_dir=SKILLS_DIR, output_dir=tmp_path / "a3")
    result = asyncio.run(agent.run({"skills": [skill_name]}))
    graphs = result.get("graph_artifacts", {}).get(skill_name, {})
    expected_graphs = [
        "skill_execution_graph", "agent_workflow_graph", "dependency_graph",
        "benchmark_comparison_graph", "file_relationship_graph",
        "tool_usage_graph", "security_coverage_graph",
    ]
    for g in expected_graphs:
        assert g in graphs, f"Missing graph: {g}"


def test_agent1_all_skills_pass(tmp_path: Path) -> None:
    if not SKILLS_DIR.exists():
        pytest.skip("skills directory not available")
    from agents.agent1 import Agent1

    agent = Agent1(skills_dir=SKILLS_DIR, output_dir=tmp_path / "a1")
    result = asyncio.run(agent.run())
    assert result["skills_analyzed"] == 26
    issues = result.get("gap_analysis", {}).get("total_issues", 0)
    assert issues == 0, f"Expected 0 issues, got {issues}"
