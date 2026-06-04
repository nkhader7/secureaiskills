"""Tests for core.parsers — multi-format skill parsing."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.parsers import SkillContext, parse_skill, parse_skills_dir

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


def test_parse_md_skill(tmp_path: Path) -> None:
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: Test skill\ntriggers:\n  - /my-skill\nreferences: {}\n---\n\n## Orchestration\nDo stuff.\n\n## Usage\n/my-skill\n",
        encoding="utf-8",
    )
    ctx = parse_skill(skill_dir / "SKILL.md")
    assert ctx.name == "my-skill"
    assert ctx.format == "md"
    assert "Orchestration" in ctx.body


def test_parse_json_skill(tmp_path: Path) -> None:
    data = {"name": "json-skill", "description": "A JSON skill", "rules": [{"id": "R1", "severity": "High"}]}
    p = tmp_path / "skill.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    ctx = parse_skill(p)
    assert ctx.name == "json-skill"
    assert ctx.format == "json"
    assert len(ctx.rules) == 1


def test_parse_yaml_skill(tmp_path: Path) -> None:
    yaml_content = "name: yaml-skill\ndescription: YAML skill\nrules:\n  - id: Y1\n    severity: Medium\n"
    p = tmp_path / "skill.yaml"
    p.write_text(yaml_content, encoding="utf-8")
    ctx = parse_skill(p)
    assert ctx.name == "yaml-skill"
    assert ctx.format == "yaml"


def test_parse_directory_with_skill_md(tmp_path: Path) -> None:
    skill_dir = tmp_path / "dir-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: dir-skill\ndescription: Dir skill\ntriggers:\n  - /dir-skill\nreferences: {}\n---\n\nBody text.\n",
        encoding="utf-8",
    )
    (skill_dir / "extra.md").write_text("extra content", encoding="utf-8")
    ctx = parse_skill(skill_dir)
    assert ctx.name == "dir-skill"
    assert "extra.md" in ctx.related_files


def test_parse_skills_dir(tmp_path: Path) -> None:
    for name in ["skill-a", "skill-b"]:
        d = tmp_path / name
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: x\ntriggers: []\nreferences: {{}}\n---\n\nBody.\n", encoding="utf-8")
    (tmp_path / "_shared").mkdir()  # should be skipped
    ctxs = parse_skills_dir(tmp_path)
    assert len(ctxs) == 2
    assert {c.name for c in ctxs} == {"skill-a", "skill-b"}


def test_unsupported_format_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.xyz"
    p.write_text("content", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        parse_skill(p)


def test_parse_real_skill_md() -> None:
    injection_dir = SKILLS_DIR / "scan-for-injection"
    if not injection_dir.exists():
        pytest.skip("skills directory not available")
    ctx = parse_skill(injection_dir)
    assert ctx.name == "scan-for-injection"
    assert len(ctx.rules) > 0
    assert ctx.template != ""
