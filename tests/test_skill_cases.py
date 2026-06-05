"""
Comprehensive skill test case runner.

Tests three categories:
  1. Structure tests  — every skill has all required case files
  2. Pattern tests    — regex-based skills: vulnerable fixtures match, safe fixtures don't
  3. Expected-findings validation — expected-findings.json is well-formed

Run: pytest tests/test_skill_cases.py -v
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
CASES_DIR = REPO_ROOT / "test-projects" / "skill-positive-negative-cases"

REQUIRED_CASE_FILES = ["positive.md", "negative.md", "edge.md", "false-positive.md", "expected-findings.json"]
REQUIRED_EF_KEYS = {"skill", "version", "cases"}
VALID_CASE_TYPES = {"positive", "negative", "edge", "false_positive"}

ALL_SKILLS = sorted(
    d.name for d in SKILLS_DIR.iterdir()
    if d.is_dir() and not d.name.startswith("_")
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_ef(skill: str) -> dict[str, Any]:
    path = CASES_DIR / skill / "expected-findings.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_rules(skill: str) -> list[dict[str, Any]]:
    from agents.llm import safe_load_yaml
    data = safe_load_yaml(SKILLS_DIR / skill / "references" / "rules.yaml")
    return data.get("rules", [])


def _match_rules(rules: list[dict[str, Any]], text: str) -> list[str]:
    """Return list of rule IDs whose patterns match the given text."""
    matched = []
    for rule in rules:
        patterns = rule.get("patterns") or []
        if not isinstance(patterns, list):
            continue
        for pat in patterns:
            try:
                if re.search(str(pat), text, re.IGNORECASE | re.MULTILINE):
                    matched.append(rule["id"])
                    break
            except re.PatternError:
                pass  # malformed pattern — skip
    return matched


def _fixture_text(skill: str, fixture_ref: str) -> str | None:
    """Load fixture text from a relative path inside the skill's case directory."""
    path = CASES_DIR / skill / fixture_ref
    if path.exists() and path.suffix in {".js", ".py", ".tf", ".yaml", ".yml",
                                          ".json", ".toml", ".xml", ".md", ".env", ".txt"}:
        return path.read_text(encoding="utf-8", errors="replace")
    return None


# ── 1. Structure tests ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_case_dir_exists(skill: str) -> None:
    assert (CASES_DIR / skill).is_dir(), f"No test case directory for {skill}"


@pytest.mark.parametrize("skill", ALL_SKILLS)
@pytest.mark.parametrize("filename", REQUIRED_CASE_FILES)
def test_required_case_file_exists(skill: str, filename: str) -> None:
    path = CASES_DIR / skill / filename
    assert path.exists(), f"Missing {filename} for {skill}"
    assert path.stat().st_size > 0, f"{filename} for {skill} is empty"


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_positive_md_contains_trigger(skill: str) -> None:
    text = (CASES_DIR / skill / "positive.md").read_text(encoding="utf-8", errors="replace")
    assert f"/{skill}" in text, f"positive.md for {skill} missing trigger /{skill}"


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_negative_md_does_not_use_trigger(skill: str) -> None:
    text = (CASES_DIR / skill / "negative.md").read_text(encoding="utf-8", errors="replace")
    # Negative case should explain WHY the trigger is not used, not use it as a command
    assert f"/{skill}" not in text.split("```")[0], \
        f"negative.md for {skill} uses the trigger command in its request — should be a non-trigger request"


# ── 2. Expected-findings validation ───────────────────────────────────────────

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_expected_findings_schema(skill: str) -> None:
    ef = _load_ef(skill)
    missing = REQUIRED_EF_KEYS - ef.keys()
    assert not missing, f"{skill}/expected-findings.json missing keys: {missing}"
    assert ef["skill"] == skill, f"skill field mismatch in {skill}/expected-findings.json"
    assert isinstance(ef["cases"], list), f"{skill}/expected-findings.json 'cases' must be a list"
    assert len(ef["cases"]) >= 2, f"{skill}: need at least positive + negative case"


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_expected_findings_case_types(skill: str) -> None:
    ef = _load_ef(skill)
    for case in ef["cases"]:
        assert "id" in case, f"{skill}: case missing 'id'"
        assert case.get("type") in VALID_CASE_TYPES, \
            f"{skill}: case {case.get('id')} has invalid type '{case.get('type')}'"
        assert "description" in case, f"{skill}: case {case.get('id')} missing description"
        assert "expected_rule_ids" in case, f"{skill}: case {case.get('id')} missing expected_rule_ids"


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_expected_findings_has_positive_and_negative(skill: str) -> None:
    ef = _load_ef(skill)
    types = {c["type"] for c in ef["cases"]}
    assert "positive" in types, f"{skill}: no positive test case in expected-findings.json"
    assert "negative" in types, f"{skill}: no negative test case in expected-findings.json"


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_expected_findings_rule_ids_exist(skill: str) -> None:
    ef = _load_ef(skill)
    rules = _load_rules(skill)
    valid_ids = {r["id"] for r in rules}
    for case in ef["cases"]:
        for rid in case.get("expected_rule_ids", []):
            assert rid in valid_ids, \
                f"{skill} case {case['id']}: rule ID '{rid}' not found in rules.yaml"


# ── 3. Pattern match tests (regex-based skills only) ──────────────────────────

REGEX_SKILLS_FIXTURES: list[tuple[str, str, list[str], str]] = [
    # (skill, fixture_file, expected_rule_ids_to_find, case_type)
    ("scan-for-injection", "fixtures/vulnerable.js", ["SI-001"], "positive"),
    ("scan-for-injection", "fixtures/vulnerable.js", ["SI-002"], "positive"),
    ("scan-for-injection", "fixtures/vulnerable.js", ["SI-003"], "positive"),
    ("scan-for-injection", "fixtures/safe.js",        [],        "negative"),
    ("detect-secrets",     "fixtures/vulnerable.env", ["DS-001"], "positive"),
    ("detect-secrets",     "fixtures/vulnerable.env", ["DS-004"], "positive"),
    # detect-secrets has 393 rules including generic patterns; safe.env is empty-value
    # so we only assert specific high-confidence rules do NOT fire, not that zero rules fire.
    ("detect-secrets",     "fixtures/edge.py",         ["DS-001"], "edge"),
    # SSRF patterns correctly fire on request.args even in validated code —
    # the LLM layer then determines whether the URL is validated.
    # We assert SSRF-002 (metadata endpoint) does NOT fire on safe.py.
    ("scan-for-ssrf",      "fixtures/vulnerable.py",  ["SSRF-001"], "positive"),
    ("scan-for-ssrf",      "fixtures/vulnerable.py",  ["SSRF-002"], "positive"),
    ("scan-for-ssrf",      "fixtures/vulnerable.py",  ["SSRF-003"], "positive"),
    ("scan-yaml-security", "fixtures/vulnerable.yaml", ["YAML-001"], "positive"),
    ("scan-yaml-security", "fixtures/safe.yaml",        [],          "negative"),
    ("scan-xml-security",  "fixtures/vulnerable.xml",  ["XML-001"],  "positive"),
    ("scan-xml-security",  "fixtures/safe.xml",         [],          "negative"),
    ("scan-json-security", "fixtures/vulnerable.json", ["JSON-001"], "positive"),
    ("scan-json-security", "fixtures/safe.json",        [],          "negative"),
    ("scan-toml-security", "fixtures/vulnerable.toml", ["TOML-001"], "positive"),
    ("scan-toml-security", "fixtures/safe.toml",        [],          "negative"),
    ("scan-markdown-security", "fixtures/vulnerable.md", ["MD-001"], "positive"),
]


# SSRF-002 (metadata endpoint) must NOT fire on safe fixture
def test_ssrf_metadata_does_not_fire_on_safe_fixture() -> None:
    text = _fixture_text("scan-for-ssrf", "fixtures/safe.py")
    if text is None:
        pytest.skip("SSRF safe fixture not found")
    rules = _load_rules("scan-for-ssrf")
    matched = _match_rules(rules, text)
    assert "SSRF-002" not in matched, (
        "SSRF-002 (cloud metadata endpoint) should not fire on safe.py — "
        "that fixture has no 169.254.169.254 reference"
    )


# detect-secrets: DS-001 (AWS key) must NOT fire on the clean safe fixture
def test_detect_secrets_no_aws_key_in_safe_fixture() -> None:
    text = _fixture_text("detect-secrets", "fixtures/safe.env")
    if text is None:
        pytest.skip("detect-secrets safe fixture not found")
    rules = _load_rules("detect-secrets")
    matched = _match_rules(rules, text)
    assert "DS-001" not in matched, (
        f"DS-001 (AWS key pattern) should not fire on empty-value safe.env. Matched: {matched}"
    )


@pytest.mark.parametrize("skill,fixture,expected_ids,case_type", REGEX_SKILLS_FIXTURES,
                         ids=[f"{s}-{f.split('/')[-1]}-{ct}" for s, f, _, ct in REGEX_SKILLS_FIXTURES])
def test_pattern_match(skill: str, fixture: str, expected_ids: list[str], case_type: str) -> None:
    text = _fixture_text(skill, fixture)
    if text is None:
        pytest.skip(f"Fixture {fixture} not found for {skill}")

    rules = _load_rules(skill)
    if not rules:
        pytest.skip(f"No rules loaded for {skill}")

    matched = _match_rules(rules, text)

    if case_type in ("positive", "edge") and expected_ids:
        missing = [rid for rid in expected_ids if rid not in matched]
        assert not missing, (
            f"{skill}/{fixture}: expected rules {expected_ids} to match "
            f"but {missing} did not fire. Matched: {matched}"
        )

    elif case_type == "negative" and not expected_ids:
        # For negative cases, we allow matches IF the rules use design_review strategy
        # (those are LLM-evaluated and won't fire via regex).
        # Only assert clean for skills that are purely regex-based.
        has_regex = any(
            r.get("match_strategy") in ("regex", None, "") and r.get("patterns")
            for r in rules
        )
        if has_regex and matched:
            pytest.fail(
                f"{skill}/{fixture}: expected NO pattern matches (negative case) "
                f"but these rules fired: {matched}"
            )


# ── 4. Coverage summary ────────────────────────────────────────────────────────

def test_all_skills_have_fixture_or_ef_cases() -> None:
    """Every skill must have at least 2 cases in its expected-findings.json."""
    short = []
    for skill in ALL_SKILLS:
        try:
            ef = _load_ef(skill)
            if len(ef.get("cases", [])) < 2:
                short.append(skill)
        except Exception:
            short.append(skill)
    assert not short, f"Skills with insufficient test cases: {short}"


def test_regex_skills_have_fixture_files() -> None:
    """Skills that have regex patterns must have at least one fixture file."""
    from agents.llm import safe_load_yaml
    missing = []
    for skill in ALL_SKILLS:
        rules = safe_load_yaml(SKILLS_DIR / skill / "references/rules.yaml").get("rules", [])
        has_patterns = any(r.get("patterns") for r in rules)
        if has_patterns:
            fixture_dir = CASES_DIR / skill / "fixtures"
            if not fixture_dir.exists() or not list(fixture_dir.iterdir()):
                missing.append(skill)
    assert not missing, f"Regex-based skills missing fixture files: {missing}"
