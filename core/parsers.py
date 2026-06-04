"""
Multi-format skill parser.

Accepts a Path to any supported skill format and returns a normalised
SkillContext dict that every agent can consume uniformly.

Supported formats: .md  .yaml  .yml  .json  .toml  .py  directory  .zip
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── SkillContext ───────────────────────────────────────────────────────────────


@dataclass
class SkillContext:
    name: str
    format: str                               # md | yaml | json | toml | py | directory | zip
    raw_text: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    rules_data: dict[str, Any] = field(default_factory=dict)
    rules: list[dict[str, Any]] = field(default_factory=list)
    template: str = ""
    file_path: str = ""
    related_files: dict[str, str] = field(default_factory=dict)   # rel-path → content
    skill_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


# ── YAML helper ───────────────────────────────────────────────────────────────


def _load_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml as _yaml  # type: ignore[import-untyped]
        return _yaml.safe_load(text) or {}
    except Exception:
        return {}


def _load_toml(text: str) -> dict[str, Any]:
    try:
        import tomllib  # Python ≥ 3.11
        return tomllib.loads(text)
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
            return tomllib.loads(text.encode())
        except ImportError:
            pass
    except Exception:
        pass
    return {}


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text.strip()
    return _load_yaml(m.group(1)), m.group(2).strip()


# ── Format-specific parsers ───────────────────────────────────────────────────


def _parse_md(path: Path) -> SkillContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = _parse_frontmatter(text)
    name = fm.get("name") or path.stem
    refs = fm.get("references") or {}
    rules_data, template = {}, ""
    rules_path = path.parent / refs.get("rules", "references/rules.yaml")
    tmpl_path = path.parent / refs.get("report_template", "references/report-template.md")
    if rules_path.exists():
        try:
            import yaml as _yaml
            rules_data = _yaml.safe_load(rules_path.read_text(encoding="utf-8", errors="replace")) or {}
        except Exception:
            rules_data = {}
    if tmpl_path.exists():
        template = tmpl_path.read_text(encoding="utf-8", errors="replace")
    return SkillContext(
        name=name,
        format="md",
        raw_text=text,
        frontmatter=fm,
        body=body,
        rules_data=rules_data,
        rules=rules_data.get("rules", []),
        template=template,
        file_path=str(path),
        skill_dir=str(path.parent),
    )


def _parse_yaml_file(path: Path) -> SkillContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    data = _load_yaml(text)
    name = data.get("name") or path.stem
    rules = data.get("rules", [])
    body = data.get("instructions") or data.get("description") or ""
    return SkillContext(
        name=name,
        format="yaml",
        raw_text=text,
        frontmatter=data,
        body=body,
        rules_data=data,
        rules=rules,
        file_path=str(path),
        skill_dir=str(path.parent),
    )


def _parse_json_file(path: Path) -> SkillContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {}
    name = data.get("name") or path.stem
    rules = data.get("rules", [])
    body = data.get("instructions") or data.get("description") or ""
    return SkillContext(
        name=name,
        format="json",
        raw_text=text,
        frontmatter=data,
        body=body,
        rules_data=data,
        rules=rules,
        file_path=str(path),
        skill_dir=str(path.parent),
    )


def _parse_toml_file(path: Path) -> SkillContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    data = _load_toml(text)
    name = data.get("name") or path.stem
    rules = data.get("rules", [])
    body = data.get("instructions") or data.get("description") or ""
    return SkillContext(
        name=name,
        format="toml",
        raw_text=text,
        frontmatter=data,
        body=body,
        rules_data=data,
        rules=rules,
        file_path=str(path),
        skill_dir=str(path.parent),
    )


def _parse_py_file(path: Path) -> SkillContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    data: dict[str, Any] = {}
    # Try extracting a top-level SKILL = {...} dict literal
    m = re.search(r"^SKILL\s*=\s*(\{.+?\})\s*$", text, re.DOTALL | re.MULTILINE)
    if m:
        try:
            data = ast.literal_eval(m.group(1))
        except Exception:
            pass
    name = data.get("name") or path.stem
    rules = data.get("rules", [])
    body = data.get("instructions") or data.get("description") or ""
    return SkillContext(
        name=name,
        format="py",
        raw_text=text,
        frontmatter=data,
        body=body,
        rules_data=data,
        rules=rules,
        file_path=str(path),
        skill_dir=str(path.parent),
    )


def _parse_directory(path: Path) -> SkillContext:
    skill_md = path / "SKILL.md"
    if skill_md.exists():
        ctx = _parse_md(skill_md)
        # Attach related files
        for f in path.rglob("*"):
            if f.is_file() and f != skill_md:
                try:
                    ctx.related_files[str(f.relative_to(path))] = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass
        return ctx
    # No SKILL.md — synthesise a context from whatever files exist
    texts: dict[str, str] = {}
    for f in sorted(path.rglob("*"))[:50]:
        if f.is_file():
            try:
                texts[str(f.relative_to(path))] = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    combined = "\n\n".join(f"# {k}\n{v}" for k, v in texts.items())
    return SkillContext(
        name=path.name,
        format="directory",
        raw_text=combined,
        body=combined[:4000],
        related_files=texts,
        file_path=str(path),
        skill_dir=str(path),
    )


# ── Public API ─────────────────────────────────────────────────────────────────


_EXT_DISPATCH = {
    ".md": _parse_md,
    ".yaml": _parse_yaml_file,
    ".yml": _parse_yaml_file,
    ".json": _parse_json_file,
    ".toml": _parse_toml_file,
    ".py": _parse_py_file,
}


def parse_skill(path: Path) -> SkillContext:
    """Parse a skill in any supported format into a SkillContext."""
    if path.is_dir():
        return _parse_directory(path)
    suffix = path.suffix.lower()
    parser = _EXT_DISPATCH.get(suffix)
    if parser is None:
        raise ValueError(f"Unsupported skill format: {suffix}")
    return parser(path)


def parse_skills_dir(directory: Path) -> list[SkillContext]:
    """Parse every skill sub-directory found under *directory*."""
    contexts = []
    if not directory.exists():
        return contexts
    for d in sorted(directory.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            try:
                contexts.append(_parse_directory(d))
            except Exception:
                pass
    return contexts
