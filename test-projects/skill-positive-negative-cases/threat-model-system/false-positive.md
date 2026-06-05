# False positive cases: threat-model-system

Patterns that superficially resemble a vulnerability but are safe.

## FP 1 — Validated / constant value

**Scenario:** Pattern appears but input is validated or value is constant.

**Request:** `/threat-model-system` on safe fixture
**Expected:** No Critical finding; if reported, severity reduced + note added.

## FP 2 — Pattern in comment or docstring

**Scenario:** Vulnerable keyword appears only in a non-executable string.

**Expected:** Info/Low at most; no Critical/High for non-executable context.

## FP 3 — Third-party library internals

**Scenario:** Pattern is inside `node_modules/`, `vendor/`, or `.venv/`.

**Expected:** Excluded from scan; no findings from vendor paths.
