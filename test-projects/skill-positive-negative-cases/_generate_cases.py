"""Generate edge.md and false-positive.md for all 26 skills."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agents.llm import safe_load_yaml  # noqa: E402

BASE = Path(__file__).parent
SKILLS_DIR = BASE.parents[1] / "skills"
FIXTURE_DIR = BASE.parent / "skill-fixture"


def make_edge(skill: str, trigger: str, subcategory: str) -> str:
    return f"""# Edge cases: {skill}

Boundary conditions where the skill fires correctly but context matters.

## Edge 1 — Pattern in test file

**Request:** `{trigger} {FIXTURE_DIR}/src`
Scan for {subcategory} issues. Note findings even inside test files.

**Expected:** Finding surfaced with test-context note; severity may be reduced.

## Edge 2 — Obfuscated / split pattern

**Scenario:** The vulnerable construct is split across lines or uses string
concatenation. A reasoning LLM should still detect the reconstructed risk.

**Expected:** Finding with "indirect evidence" qualifier.

## Edge 3 — Empty or binary file

**Expected:** Skill skips gracefully, no false positives, report notes skipped files.
"""


def make_fp(skill: str, trigger: str) -> str:
    return f"""# False positive cases: {skill}

Patterns that superficially resemble a vulnerability but are safe.

## FP 1 — Validated / constant value

**Scenario:** Pattern appears but input is validated or value is constant.

**Request:** `{trigger}` on safe fixture
**Expected:** No Critical finding; if reported, severity reduced + note added.

## FP 2 — Pattern in comment or docstring

**Scenario:** Vulnerable keyword appears only in a non-executable string.

**Expected:** Info/Low at most; no Critical/High for non-executable context.

## FP 3 — Third-party library internals

**Scenario:** Pattern is inside `node_modules/`, `vendor/`, or `.venv/`.

**Expected:** Excluded from scan; no findings from vendor paths.
"""


for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
        continue
    skill = skill_dir.name
    rules_data = safe_load_yaml(skill_dir / "references/rules.yaml")
    rules = rules_data.get("rules", [])
    subcategory = rules[0].get("category", skill) if rules else skill
    trigger = f"/{skill}"

    case_dir = BASE / skill
    case_dir.mkdir(exist_ok=True)

    edge_path = case_dir / "edge.md"
    if not edge_path.exists():
        edge_path.write_text(make_edge(skill, trigger, subcategory), encoding="utf-8")

    fp_path = case_dir / "false-positive.md"
    if not fp_path.exists():
        fp_path.write_text(make_fp(skill, trigger), encoding="utf-8")

print(f"Done. edge.md: {len(list(BASE.rglob('edge.md')))},  false-positive.md: {len(list(BASE.rglob('false-positive.md')))}")
