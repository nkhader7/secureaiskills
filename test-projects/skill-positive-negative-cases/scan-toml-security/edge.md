# Edge cases: scan-toml-security

Boundary conditions where the skill fires correctly but context matters.

## Edge 1 — Pattern in test file

**Request:** `/scan-toml-security D:\Download\CascadeProjects\secureaiskills\test-projects\skill-fixture/src`
Scan for Secrets issues. Note findings even inside test files.

**Expected:** Finding surfaced with test-context note; severity may be reduced.

## Edge 2 — Obfuscated / split pattern

**Scenario:** The vulnerable construct is split across lines or uses string
concatenation. A reasoning LLM should still detect the reconstructed risk.

**Expected:** Finding with "indirect evidence" qualifier.

## Edge 3 — Empty or binary file

**Expected:** Skill skips gracefully, no false positives, report notes skipped files.
