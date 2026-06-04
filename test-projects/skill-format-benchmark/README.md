# Security Skill Format Benchmark

Benchmarks five security skill definition formats — **Markdown, YAML, TOML, JSON, and Inline-YAML** — across two skills (`detect-secrets` and `scan-iac-security`) and their purpose-built test fixtures.

Produces a live Chart.js dashboard at `http://localhost:8080` and an interactive simulator at `http://localhost:8080/simulator.html`.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.11 or later (3.14 tested) |
| pyyaml | `pip install pyyaml` |
| Browser | Any modern browser |

`tomllib` is bundled with Python 3.11+. No other dependencies are needed.

---

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/nkhader7/secureaiskills.git
cd secureaiskills

# 2. Install Python dependencies
pip install -r test-projects/skill-format-benchmark/requirements.txt

# 3. Navigate to the benchmark directory
cd test-projects/skill-format-benchmark

# 4. Run the benchmark (generates results/benchmark-results.json)
python benchmark.py

# 5. Serve the dashboard (opens browser automatically)
python serve.py
```

The dashboard opens at **http://localhost:8080**
The simulator opens at **http://localhost:8080/simulator.html**

Press `Ctrl+C` to stop the server.

---

## Streamlit security skill lab

For the interactive skill writer, skill scanner, test-project builder, and benchmark runner:

```bash
cd test-projects/skill-format-benchmark
streamlit run streamlit_app.py
```

The Streamlit app includes:

| Tab | Capability |
|---|---|
| Benchmark | Load or re-run `benchmark.py`, compare parse time, scan time, detection rate, findings, and efficiency |
| Skill Writer | Draft a security skill, scan it for safety issues, and generate Markdown, YAML, TOML, JSON, XML, and Inline-YAML variants |
| Test Project Builder | Generate a selected-skill test project manifest with TP, FP, FN, TN, all severities, expected findings, trace requirements, and result metrics |
| Requirements | Deep checklist for building security skills, scanning skills, creating fixtures, and validating results |

Use the static HTML dashboard for sharing results and the Streamlit app for hands-on testing and iteration.

---

## What the benchmark measures

`benchmark.py` runs 50 parse iterations per format and one scan pass per format per skill, recording:

| Metric | Description |
|---|---|
| `parse_avg_ms` | Average parse time across 50 runs |
| `parse_p95_ms` | 95th-percentile parse time (consistency measure) |
| `scan_ms` | Time to run compiled regex across all fixture files |
| `rule_count` | Number of rules actually extracted by the parser |
| `total_findings` | Regex matches found in the fixture |
| `detection_rate` | % of rules that fired at least one match |
| `efficiency_score` | Composite: 25% parse + 35% detection + 40% quality |
| `quality_scores` | Seven structural dimensions scored 0–10 |

---

## Project layout

```
skill-format-benchmark/
  benchmark.py              # benchmark runner — produces results/benchmark-results.json
  serve.py                  # HTTP server — serves app/ and results/ on port 8080
  simulator.html            # browser-side skill format simulator
  app/
    index.html              # Chart.js benchmark dashboard
  results/
    benchmark-results.json  # generated output consumed by the dashboard
  skill-variants/
    detect-secrets.md           # Markdown variant
    detect-secrets.yaml         # YAML variant
    detect-secrets.toml         # TOML variant
    detect-secrets.json         # JSON variant
    detect-secrets-inline.yaml  # Inline-YAML variant
    scan-iac-security.md
    scan-iac-security.yaml
    scan-iac-security.toml
    scan-iac-security.json
    scan-iac-security-inline.yaml

../skill-fixture/           # detect-secrets test fixture (55 files)
../skill-iac-fixture/       # IaC test fixture (12 files — Terraform, K8s, CFN, Bicep, Pulumi)
```

---

## Re-running the benchmark

```bash
# Re-run benchmark and restart server
python benchmark.py && python serve.py
```

The server always serves the latest `results/benchmark-results.json`. If the file already exists, `serve.py` skips re-running the benchmark. Delete it or re-run `benchmark.py` manually to refresh.

---

## Dashboard sections

| # | Section | What it shows |
|---|---|---|
| 1 | Performance | Parse avg, parse spread (min/avg/p95/max), scan time |
| 2 | Detection Quality | Detection rate %, total findings, severity breakdown |
| 3 | Structural Quality | Radar chart (7 dimensions), file size, rules extracted |
| 4 | Composite Efficiency | Weighted score 0–10 per format |
| 5 | Full Comparison | All metrics table with best-value highlights + winner callout |
| 6 | Sample Findings | First 10 Critical/High matches from the best format |

Switch between `detect-secrets` and `scan-iac-security` using the tabs in the top bar.

---

## Key findings

| Format | Parse avg | Detection | Efficiency | Best for |
|---|---|---|---|---|
| **JSON** | ~0.05 ms | 100% | **8.78** | Programmatic generation, max tooling |
| **TOML** | ~0.5 ms | 100% | 8.33 | Human-readable config-style skills |
| **MD** | ~0.4 ms | 90%* | 8.02 | Human review in GitHub |
| YAML | ~4–6 ms | 100% | 6.41 | Production skills (with split files) |
| Inline-YAML | ~5 ms | 100% | 6.59 | Small self-contained skills |

\* MD misses ~10% of rules because its regex extractor breaks on patterns containing commas inside quantifiers like `{24,}`. The production `SKILL.md` format avoids this by keeping rules in a separate `rules.yaml`.

**Recommended pattern for production security skills:**
- `SKILL.md` — orchestration prose, human-readable, LLM-friendly
- `references/rules.yaml` — machine-parseable rule catalog

---

## Adding a new skill to the benchmark

1. Create five variant files in `skill-variants/` named `<skill-name>.md`, `.yaml`, `.toml`, `.json`, and `-inline.yaml`
2. Create a fixture directory at `../skill-<name>-fixture/` with intentionally vulnerable files
3. Add a new entry to the `SKILLS` list in `benchmark.py`:

```python
{
    "skill_id": "your-skill-name",
    "fixture":  BENCH_DIR.parent / "skill-your-name-fixture",
    "variants": [
        ("md",          "your-skill-name.md",          parse_md),
        ("yaml",        "your-skill-name.yaml",         parse_yaml),
        ("toml",        "your-skill-name.toml",         parse_toml),
        ("json",        "your-skill-name.json",         parse_json),
        ("inline-yaml", "your-skill-name-inline.yaml",  parse_inline_yaml),
    ],
},
```

4. Re-run `python benchmark.py && python serve.py`
