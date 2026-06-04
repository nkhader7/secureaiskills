"""Shared pytest fixtures for the SecureAI Skills test suite."""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


@pytest.fixture()
def sample_skill_md_bytes() -> bytes:
    return (
        b"---\n"
        b"name: test-skill\n"
        b"description: A test security skill\n"
        b"triggers:\n"
        b"  - /test-skill\n"
        b"references: {}\n"
        b"---\n\n"
        b"## Orchestration\n\nScan target files.\n\n"
        b"## Usage\n\n`/test-skill`\n"
    )


@pytest.fixture()
def sample_skill_zip(sample_skill_md_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("skills/test-skill/SKILL.md", sample_skill_md_bytes.decode())
    return buf.getvalue()


@pytest.fixture()
def minimal_report() -> dict:
    return {
        "overall_risk": "low",
        "pass_fail_decision": "pass",
        "coverage_map": {"coverage_score": 0.74},
        "compliance_report": [{"governance_valid": True}],
        "ci_cd_report": [{"validation_score": 85}],
        "benchmark_report": [{"benchmark_score": 8.5}],
        "security_report": [],
        "total_findings": 0,
    }


@pytest.fixture()
def scan_injection_dir() -> Path:
    return SKILLS_DIR / "scan-for-injection"
