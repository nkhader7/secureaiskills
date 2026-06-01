# Skill Positive/Negative Cases

This directory contains explicit routing test prompts for every skill in `../../skills`.

Each skill has two files:

- `positive.md`: a request that should invoke the skill, usually by using the slash trigger and pointing at `../skill-fixture`.
- `negative.md`: a nearby but non-security editorial request that should not invoke the skill.

The cases are intended for skill-selection and regression tests. The positive cases reuse evidence already tracked in `../skill-fixture/expected-findings.json`; the negative cases are intentionally bland so a router can verify that security skills are not selected for unrelated work.

See `manifest.json` for the complete case list.
