"""
Skill Format Benchmark
Measures parse time, detection rate, rule extraction, and structural quality
for MD, YAML, TOML, JSON, and inline-YAML skill formats.
Runs two skills: detect-secrets (general fixture) and scan-iac-security (IaC fixture).
Outputs results/benchmark-results.json consumed by the web app.
"""

import json
import re
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml not installed — run: pip install pyyaml")

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# ─── paths ───────────────────────────────────────────────────────────────────

BENCH_DIR = Path(__file__).parent
VARIANTS = BENCH_DIR / "skill-variants"
RESULTS_DIR = BENCH_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

FIXTURE_SECRETS = BENCH_DIR.parent / "skill-fixture"
FIXTURE_IAC = BENCH_DIR.parent / "skill-iac-fixture"

SKIP_EXTS = {
    ".lock",
    ".png",
    ".jpg",
    ".svg",
    ".gif",
    ".woff",
    ".ttf",
    ".ico",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".pyc",
    ".zip",
}
SKIP_FILES = {"package-lock.json", "yarn.lock", "poetry.lock"}
SKIP_DIRS = {".terraform", "node_modules", ".git", "__pycache__"}

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}

RUNS = 50  # parse-timing repetitions

# ─── file collection ─────────────────────────────────────────────────────────


def collect_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix in SKIP_EXTS or p.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        files.append(p)
    return sorted(files)


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []


# ─── parsers — each returns (rules, parse_ms, meta) ──────────────────────────


def parse_md(path: Path):
    t0 = time.perf_counter()
    text = path.read_text(encoding="utf-8")
    rules = []
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    meta = {}
    if fm_match:
        try:
            meta = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            pass

    section_re = re.compile(
        r"###\s+(\w[^\n]+?)\s+—\s+(.+?)\s+\((Critical|High|Medium|Low|Info)\)\n(.*?)(?=###|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    pat_line_re = re.compile(r"^Patterns?:\s*(.+)$", re.MULTILINE)
    backtick_re = re.compile(r"`([^`]+)`")
    remediation_re = re.compile(r"^Remediation:\s*(.+)$", re.MULTILINE)

    for m in section_re.finditer(text):
        rule_id, name, severity, body = m.groups()
        pat_match = pat_line_re.search(body)
        rem_match = remediation_re.search(body)
        if not pat_match:
            continue
        patterns = backtick_re.findall(pat_match.group(1))
        rules.append(
            {
                "id": rule_id.strip(),
                "name": name,
                "severity": severity,
                "patterns": patterns,
                "remediation": rem_match.group(1).strip() if rem_match else "",
            }
        )
    elapsed = (time.perf_counter() - t0) * 1000
    return rules, elapsed, meta


def parse_yaml(path: Path):
    t0 = time.perf_counter()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    elapsed = (time.perf_counter() - t0) * 1000
    return data.get("rules", []), elapsed, data


def parse_toml(path: Path):
    if tomllib is None:
        return [], 0.0, {}
    t0 = time.perf_counter()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    elapsed = (time.perf_counter() - t0) * 1000
    return data.get("rules", []), elapsed, data


def parse_json(path: Path):
    t0 = time.perf_counter()
    data = json.loads(path.read_text(encoding="utf-8"))
    elapsed = (time.perf_counter() - t0) * 1000
    return data.get("rules", []), elapsed, data


def parse_inline_yaml(path: Path):
    return parse_yaml(path)


# ─── detection engine ─────────────────────────────────────────────────────────


def compile_rules(rules: list) -> list:
    compiled = []
    for rule in rules:
        rxs = []
        for p in rule.get("patterns", []):
            try:
                rxs.append(re.compile(p))
            except re.error:
                pass
        compiled.append({**rule, "_rxs": rxs})
    return compiled


def scan_files(compiled_rules: list, files: list, fixture_root: Path) -> list:
    findings = []
    for fpath in files:
        for lineno, line in enumerate(read_lines(fpath), 1):
            for rule in compiled_rules:
                for rx in rule["_rxs"]:
                    if rx.search(line):
                        findings.append(
                            {
                                "file": str(fpath.relative_to(fixture_root)),
                                "line": lineno,
                                "rule_id": rule.get("id", "?"),
                                "rule_name": rule.get("name", "?"),
                                "severity": rule.get("severity", "Info"),
                                "snippet": rx.sub("***REDACTED***", line.strip()),
                            }
                        )
                        break
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["file"], f["line"]))
    return findings


# ─── structural quality scoring ──────────────────────────────────────────────

QUALITY = {
    "md": {
        "readability": 9,
        "machine_parse": 5,
        "rule_density": 6,
        "extensibility": 5,
        "tooling": 9,
        "colocation": 7,
        "fragility": 4,
    },
    "yaml": {
        "readability": 7,
        "machine_parse": 9,
        "rule_density": 8,
        "extensibility": 8,
        "tooling": 7,
        "colocation": 6,
        "fragility": 6,
    },
    "toml": {
        "readability": 8,
        "machine_parse": 8,
        "rule_density": 5,
        "extensibility": 6,
        "tooling": 6,
        "colocation": 5,
        "fragility": 8,
    },
    "json": {
        "readability": 5,
        "machine_parse": 10,
        "rule_density": 4,
        "extensibility": 9,
        "tooling": 10,
        "colocation": 4,
        "fragility": 7,
    },
    "inline-yaml": {
        "readability": 6,
        "machine_parse": 9,
        "rule_density": 9,
        "extensibility": 7,
        "tooling": 7,
        "colocation": 10,
        "fragility": 6,
    },
}

# ─── per-skill variant configs ────────────────────────────────────────────────

SKILLS = [
    {
        "skill_id": "detect-secrets",
        "fixture": FIXTURE_SECRETS,
        "variants": [
            ("md", "detect-secrets.md", parse_md),
            ("yaml", "detect-secrets.yaml", parse_yaml),
            ("toml", "detect-secrets.toml", parse_toml),
            ("json", "detect-secrets.json", parse_json),
            ("inline-yaml", "detect-secrets-inline.yaml", parse_inline_yaml),
        ],
    },
    {
        "skill_id": "scan-iac-security",
        "fixture": FIXTURE_IAC,
        "variants": [
            ("md", "scan-iac-security.md", parse_md),
            ("yaml", "scan-iac-security.yaml", parse_yaml),
            ("toml", "scan-iac-security.toml", parse_toml),
            ("json", "scan-iac-security.json", parse_json),
            ("inline-yaml", "scan-iac-security-inline.yaml", parse_inline_yaml),
        ],
    },
]

# ─── core benchmark function ──────────────────────────────────────────────────


def benchmark_format(label: str, filename: str, parser_fn, fixture_root: Path) -> dict:
    path = VARIANTS / filename
    if not path.exists():
        return {"format": label, "error": f"{filename} not found"}

    parse_times = []
    rules, meta = [], {}
    for _ in range(RUNS):
        try:
            rules, elapsed, meta = parser_fn(path)
            parse_times.append(elapsed)
        except Exception as exc:
            return {"format": label, "error": str(exc)}

    avg_ms = round(sum(parse_times) / len(parse_times), 4)
    min_ms = round(min(parse_times), 4)
    max_ms = round(max(parse_times), 4)
    p95_ms = round(sorted(parse_times)[int(RUNS * 0.95)], 4)

    fixture_files = collect_files(fixture_root)
    compiled = compile_rules(rules)

    t0 = time.perf_counter()
    findings = scan_files(compiled, fixture_files, fixture_root)
    scan_ms = round((time.perf_counter() - t0) * 1000, 2)

    sev_counts = {}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    rules_fired = len({f["rule_id"] for f in findings})
    detection_rate = round(rules_fired / max(len(rules), 1) * 100, 1)

    # efficiency score: weighted composite (parse speed, detection, quality)
    parse_score = max(0, 10 - avg_ms * 2)  # lower parse → higher score
    det_score = detection_rate / 10  # 0-10
    qual_total = sum(QUALITY.get(label, {}).values())
    qual_score = qual_total / 7  # avg across 7 dimensions
    efficiency = round((parse_score * 0.25 + det_score * 0.35 + qual_score * 0.40), 2)

    return {
        "format": label,
        "file": filename,
        "file_bytes": path.stat().st_size,
        "file_lines": len(path.read_text(encoding="utf-8").splitlines()),
        "rule_count": len(rules),
        "parse_avg_ms": avg_ms,
        "parse_min_ms": min_ms,
        "parse_max_ms": max_ms,
        "parse_p95_ms": p95_ms,
        "scan_ms": scan_ms,
        "files_scanned": len(fixture_files),
        "total_findings": len(findings),
        "rules_fired": rules_fired,
        "detection_rate": detection_rate,
        "severity_counts": sev_counts,
        "quality_scores": QUALITY.get(label, {}),
        "efficiency_score": efficiency,
        "top_findings": findings[:10],
    }


# ─── main ─────────────────────────────────────────────────────────────────────


def main():
    if tomllib is None:
        print("WARNING: tomllib/tomli not found — TOML parse times will show 0 ms\n")

    all_skills = []

    for skill_cfg in SKILLS:
        sid = skill_cfg["skill_id"]
        fixture = skill_cfg["fixture"]
        variants = skill_cfg["variants"]

        files = collect_files(fixture)
        print(f"\n=== {sid} === fixture: {fixture.name}  files: {len(files)}")

        results = []
        for label, filename, parser_fn in variants:
            print(f"  {label:15s} ({filename}) ...", end=" ", flush=True)
            r = benchmark_format(label, filename, parser_fn, fixture)
            results.append(r)
            if "error" in r:
                print(f"ERROR: {r['error']}")
            else:
                print(
                    f"rules={r['rule_count']}  findings={r['total_findings']}  "
                    f"parse={r['parse_avg_ms']}ms  scan={r['scan_ms']}ms  "
                    f"det={r['detection_rate']}%  eff={r['efficiency_score']}"
                )

        all_skills.append(
            {
                "skill_id": sid,
                "fixture": str(fixture),
                "files_scanned": len(files),
                "formats": results,
            }
        )

    output = {
        "benchmark_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parse_runs": RUNS,
        "skills": all_skills,
        # keep top-level "formats" for backward-compat with existing web app
        "formats": all_skills[0]["formats"] if all_skills else [],
        "files_scanned": all_skills[0]["files_scanned"] if all_skills else 0,
    }

    out = RESULTS_DIR / "benchmark-results.json"
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nResults -> {out}")


if __name__ == "__main__":
    main()
