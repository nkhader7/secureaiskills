#!/usr/bin/env python3
"""
Benchmark equivalent detect-secrets skill definitions across serialization formats.

The benchmark isolates skill packaging overhead from detection logic:
- each format carries the same detect-secrets body, metadata, rules, and template
- each run parses the packaged skill, compiles the same regex rules, and scans the
  same fixture targets
- the generated HTML dashboard embeds the results and draws charts without any
  external JavaScript dependency
"""

from __future__ import annotations

import html
import json
import re
import statistics
import time
import tomllib
import warnings
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

FIXTURE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = FIXTURE_ROOT.parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "detect-secrets"
RESULTS_ROOT = FIXTURE_ROOT / "results" / "skill-format-benchmark"
SKILL_MD = SKILL_DIR / "SKILL.md"
RULES_YAML = SKILL_DIR / "references" / "rules.yaml"
TEMPLATE_MD = SKILL_DIR / "references" / "report-template.md"
EXPECTED_FINDINGS = FIXTURE_ROOT / "expected-findings.json"


@dataclass(frozen=True)
class PackagedSkill:
    label: str
    extension: str
    text: str

    @property
    def file_name(self) -> str:
        return f"detect-secrets.skill.{self.extension}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_md(text: str) -> dict[str, Any]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md frontmatter was not found")

    metadata = yaml.safe_load(match.group(1)) or {}
    return {
        "metadata": metadata,
        "body": match.group(2).strip(),
    }


def load_canonical_skill() -> dict[str, Any]:
    skill = parse_skill_md(read_text(SKILL_MD))
    rules = yaml.safe_load(read_text(RULES_YAML)) or {}
    template = read_text(TEMPLATE_MD)
    return {
        "name": skill["metadata"].get("name", "detect-secrets"),
        "description": skill["metadata"].get("description", ""),
        "triggers": skill["metadata"].get("triggers", []),
        "references": skill["metadata"].get("references", {}),
        "body": skill["body"],
        "rules": rules,
        "report_template": template,
    }


def toml_quote(value: str) -> str:
    return json.dumps(value)


def toml_multiline(value: str) -> str:
    escaped = value.replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}\n"""'


def to_toml(skill: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("[skill]")
    lines.append(f"name = {toml_quote(skill['name'])}")
    lines.append(f"description = {toml_quote(skill['description'])}")
    lines.append("triggers = [" + ", ".join(toml_quote(item) for item in skill["triggers"]) + "]")
    lines.append(f"body = {toml_multiline(skill['body'])}")
    lines.append(f"report_template = {toml_multiline(skill['report_template'])}")
    lines.append("")
    lines.append("[skill.references]")
    for key, value in skill["references"].items():
        lines.append(f"{key} = {toml_quote(str(value))}")
    lines.append("")
    lines.append("[rules]")
    lines.append(f"version = {toml_quote(str(skill['rules'].get('version', '1.0')))}")
    lines.append(f"default_match_strategy = {toml_quote(str(skill['rules'].get('default_match_strategy', 'regex')))}")

    for rule in skill["rules"].get("rules", []):
        lines.append("")
        lines.append("[[rules.items]]")
        for key in ("id", "severity", "category", "name", "description", "remediation"):
            lines.append(f"{key} = {toml_quote(str(rule.get(key, '')))}")
        if rule.get("match_strategy"):
            lines.append(f"match_strategy = {toml_quote(str(rule['match_strategy']))}")
        patterns = [str(pattern) for pattern in rule.get("patterns", [])]
        lines.append("patterns = [" + ", ".join(toml_quote(pattern) for pattern in patterns) + "]")
        source = rule.get("source") or {}
        if source:
            lines.append("[rules.items.source]")
            for key, value in source.items():
                lines.append(f"{key} = {toml_quote(str(value))}")

    return "\n".join(lines) + "\n"


def append_xml_text(parent: ET.Element, tag: str, value: str) -> None:
    child = ET.SubElement(parent, tag)
    child.text = value


def to_xml(skill: dict[str, Any]) -> str:
    root = ET.Element("secureaiSkill")
    metadata = ET.SubElement(root, "metadata")
    append_xml_text(metadata, "name", skill["name"])
    append_xml_text(metadata, "description", skill["description"])
    triggers = ET.SubElement(metadata, "triggers")
    for trigger in skill["triggers"]:
        append_xml_text(triggers, "trigger", str(trigger))
    references = ET.SubElement(metadata, "references")
    for key, value in skill["references"].items():
        ref = ET.SubElement(references, "reference", {"name": str(key)})
        ref.text = str(value)

    append_xml_text(root, "body", skill["body"])
    append_xml_text(root, "reportTemplate", skill["report_template"])

    rules_node = ET.SubElement(
        root,
        "rules",
        {
            "version": str(skill["rules"].get("version", "1.0")),
            "defaultMatchStrategy": str(skill["rules"].get("default_match_strategy", "regex")),
        },
    )
    for rule in skill["rules"].get("rules", []):
        rule_node = ET.SubElement(rules_node, "rule")
        for key in ("id", "severity", "category", "name", "description", "remediation"):
            append_xml_text(rule_node, key, str(rule.get(key, "")))
        if rule.get("match_strategy"):
            append_xml_text(rule_node, "matchStrategy", str(rule["match_strategy"]))
        patterns = ET.SubElement(rule_node, "patterns")
        for pattern in rule.get("patterns", []):
            append_xml_text(patterns, "pattern", str(pattern))

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def package_skills(skill: dict[str, Any]) -> list[PackagedSkill]:
    yaml_text = yaml.safe_dump(skill, sort_keys=False, allow_unicode=False)
    json_text = json.dumps(skill, indent=2, ensure_ascii=True) + "\n"
    md_text = read_text(SKILL_MD)
    return [
        PackagedSkill("Markdown + YAML frontmatter", "md", md_text),
        PackagedSkill("YAML", "yaml", yaml_text),
        PackagedSkill("TOML", "toml", to_toml(skill)),
        PackagedSkill("JSON", "json", json_text),
        PackagedSkill("XML", "xml", to_xml(skill)),
    ]


def normalize_toml(data: dict[str, Any]) -> dict[str, Any]:
    skill = data["skill"]
    rules = data["rules"]
    return {
        "name": skill["name"],
        "description": skill["description"],
        "triggers": skill["triggers"],
        "references": skill.get("references", {}),
        "body": skill["body"],
        "report_template": skill["report_template"],
        "rules": {
            "version": rules.get("version", "1.0"),
            "default_match_strategy": rules.get("default_match_strategy", "regex"),
            "rules": rules.get("items", []),
        },
    }


def parse_xml(text: str) -> dict[str, Any]:
    root = ET.fromstring(text)
    metadata = root.find("metadata")
    rules_node = root.find("rules")
    if metadata is None or rules_node is None:
        raise ValueError("XML skill missing metadata or rules")

    references: dict[str, str] = {}
    refs_node = metadata.find("references")
    if refs_node is not None:
        for ref in refs_node.findall("reference"):
            references[ref.attrib["name"]] = ref.text or ""

    rules: list[dict[str, Any]] = []
    for rule_node in rules_node.findall("rule"):
        rule: dict[str, Any] = {}
        for key in ("id", "severity", "category", "name", "description", "remediation"):
            rule[key] = rule_node.findtext(key, "")
        match_strategy = rule_node.findtext("matchStrategy")
        if match_strategy:
            rule["match_strategy"] = match_strategy
        patterns_node = rule_node.find("patterns")
        rule["patterns"] = (
            [pattern.text or "" for pattern in patterns_node.findall("pattern")] if patterns_node is not None else []
        )
        rules.append(rule)

    return {
        "name": metadata.findtext("name", ""),
        "description": metadata.findtext("description", ""),
        "triggers": [item.text or "" for item in metadata.findall("./triggers/trigger")],
        "references": references,
        "body": root.findtext("body", ""),
        "report_template": root.findtext("reportTemplate", ""),
        "rules": {
            "version": rules_node.attrib.get("version", "1.0"),
            "default_match_strategy": rules_node.attrib.get("defaultMatchStrategy", "regex"),
            "rules": rules,
        },
    }


def parse_packaged_skill(packaged: PackagedSkill) -> dict[str, Any]:
    if packaged.extension == "md":
        parsed = parse_skill_md(packaged.text)
        return {
            "name": parsed["metadata"]["name"],
            "description": parsed["metadata"].get("description", ""),
            "triggers": parsed["metadata"].get("triggers", []),
            "references": parsed["metadata"].get("references", {}),
            "body": parsed["body"],
            "report_template": read_text(TEMPLATE_MD),
            "rules": yaml.safe_load(read_text(RULES_YAML)) or {},
        }
    if packaged.extension == "yaml":
        return yaml.safe_load(packaged.text) or {}
    if packaged.extension == "toml":
        return normalize_toml(tomllib.loads(packaged.text))
    if packaged.extension == "json":
        return json.loads(packaged.text)
    if packaged.extension == "xml":
        return parse_xml(packaged.text)
    raise ValueError(f"Unsupported format: {packaged.extension}")


def compile_rules(skill: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    compiled: list[dict[str, Any]] = []
    invalid = 0
    default_strategy = skill["rules"].get("default_match_strategy", "regex")
    for rule in skill["rules"].get("rules", []):
        strategy = rule.get("match_strategy", default_strategy)
        if strategy != "regex":
            continue
        for pattern in rule.get("patterns", []):
            try:
                compiled.append(
                    {
                        "id": rule.get("id", "unknown"),
                        "severity": rule.get("severity", "Info"),
                        "pattern": re.compile(str(pattern)),
                    }
                )
            except re.error:
                invalid += 1
    return compiled, invalid


def scan_targets(compiled_rules: list[dict[str, Any]], targets: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for relative in targets:
        target = FIXTURE_ROOT / relative
        text = read_text(target)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule in compiled_rules:
                match = rule["pattern"].search(line)
                if not match:
                    continue
                key = (relative, line_number, rule["id"])
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    {
                        "file": relative,
                        "line": line_number,
                        "rule_id": rule["id"],
                        "severity": rule["severity"],
                    }
                )
    return findings


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, round((len(ordered) - 1) * pct))
    return ordered[idx]


def benchmark_format(packaged: PackagedSkill, targets: list[str], signals: list[str], rounds: int) -> dict[str, Any]:
    parse_ms: list[float] = []
    compile_ms: list[float] = []
    scan_ms: list[float] = []
    total_ms: list[float] = []
    last_findings: list[dict[str, Any]] = []
    invalid_patterns = 0
    rule_count = 0
    pattern_count = 0

    for _ in range(rounds):
        t0 = time.perf_counter()
        parsed = parse_packaged_skill(packaged)
        t1 = time.perf_counter()
        compiled, invalid_patterns = compile_rules(parsed)
        t2 = time.perf_counter()
        last_findings = scan_targets(compiled, targets)
        t3 = time.perf_counter()

        rule_count = len(parsed["rules"].get("rules", []))
        pattern_count = len(compiled)
        parse_ms.append((t1 - t0) * 1000)
        compile_ms.append((t2 - t1) * 1000)
        scan_ms.append((t3 - t2) * 1000)
        total_ms.append((t3 - t0) * 1000)

    combined_targets = "\n".join(read_text(FIXTURE_ROOT / target) for target in targets)
    true_positives = sum(1 for signal in signals if signal in combined_targets)

    return {
        "format": packaged.extension.upper(),
        "label": packaged.label,
        "fileName": packaged.file_name,
        "bytes": len(packaged.text.encode("utf-8")),
        "rules": rule_count,
        "compiledPatterns": pattern_count,
        "invalidPatterns": invalid_patterns,
        "expectedSignals": len(signals),
        "signalsPresent": true_positives,
        "findings": len(last_findings),
        "recall": true_positives / len(signals) if signals else 0,
        "parseMs": round(statistics.mean(parse_ms), 3),
        "compileMs": round(statistics.mean(compile_ms), 3),
        "scanMs": round(statistics.mean(scan_ms), 3),
        "totalMs": round(statistics.mean(total_ms), 3),
        "p95TotalMs": round(percentile(total_ms, 0.95), 3),
    }


def quality_score(row: dict[str, Any]) -> float:
    accuracy = row["recall"] * 30
    authoring_fit = {"md": 45, "yaml": 30, "toml": 20, "json": 15, "xml": 5}.get(row["format"].lower(), 5)
    compactness = max(0, 20 - (row["bytes"] / 20_000))
    parse_speed = max(0, 5 - (row["parseMs"] / 50))
    return round(accuracy + authoring_fit + compactness + parse_speed, 1)


def recommendation(results: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(
        ({**row, "qualityScore": quality_score(row)} for row in results),
        key=lambda row: (-row["qualityScore"], row["totalMs"]),
    )
    fastest = min(results, key=lambda row: row["totalMs"])
    smallest = min(results, key=lambda row: row["bytes"])
    best_structure = next(row for row in ranked if row["format"] == "MD")
    return {
        "bestFormat": best_structure["label"],
        "bestFileName": best_structure["fileName"],
        "fastestRuntimeFormat": fastest["label"],
        "fastestRuntimeMs": fastest["totalMs"],
        "smallestFormat": smallest["label"],
        "smallestBytes": smallest["bytes"],
        "rationale": [
            (
                "Keep SKILL.md as the human-readable orchestration contract "
                "with YAML frontmatter."
            ),
            (
                "Keep large rule sets in references/rules.yaml so rules can be "
                "validated, diffed, and shared independently."
            ),
            (
                "Keep report output in references/report-template.md to avoid "
                "mixing scanner logic with presentation."
            ),
            (
                "Use JSON or XML only for generated indexes or machine exchange; "
                "use TOML for small hand-edited configs."
            ),
        ],
        "securitySkillStructure": [
            (
                "SKILL.md: name, description, triggers, references, orchestration, "
                "usage, evidence rules, false-positive handling."
            ),
            (
                "references/rules.yaml: version, default_match_strategy, rule IDs, "
                "severity, category, patterns, source, remediation."
            ),
            (
                "references/report-template.md: required placeholders, summary "
                "table, evidence rows, remediation, references."
            ),
            (
                "tests or fixture manifest: positive and negative cases with "
                "expected signals and target paths."
            ),
            (
                "results: generated benchmark JSON and dashboard HTML, not "
                "hand-maintained evidence."
            ),
        ],
        "ranked": ranked,
    }


def svg_bar_chart(rows: list[dict[str, Any]], metric: str, title: str, suffix: str) -> str:
    width = 760
    height = 320
    left = 150
    top = 48
    bar_h = 34
    gap = 18
    max_value = max(row[metric] for row in rows) or 1
    lines = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="22" class="chart-title">{html.escape(title)}</text>',
    ]
    for index, row in enumerate(rows):
        y = top + index * (bar_h + gap)
        value = row[metric]
        bar_w = max(2, (value / max_value) * (width - left - 120))
        lines.append(f'<text x="0" y="{y + 22}" class="axis-label">{html.escape(row["format"])}</text>')
        lines.append(
            f'<rect x="{left}" y="{y}" width="{bar_w:.2f}" height="{bar_h}" rx="4" class="bar bar-{index}"></rect>'
        )
        lines.append(f'<text x="{left + bar_w + 10:.2f}" y="{y + 22}" class="value-label">{value}{suffix}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def render_dashboard(payload: dict[str, Any]) -> str:
    results = payload["results"]
    ranked = payload["recommendation"]["ranked"]
    fastest = sorted(results, key=lambda row: row["totalMs"])
    smallest = sorted(results, key=lambda row: row["bytes"])
    best = next(row for row in ranked if row["format"] == "MD")
    fastest_row = fastest[0]
    smallest_row = smallest[0]

    rows_html = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['label'])}</td>"
        f"<td>{row['bytes']:,}</td>"
        f"<td>{row['parseMs']}</td>"
        f"<td>{row['compileMs']}</td>"
        f"<td>{row['scanMs']}</td>"
        f"<td>{row['totalMs']}</td>"
        f"<td>{row['findings']}</td>"
        f"<td>{row['signalsPresent']}/{row['expectedSignals']}</td>"
        "</tr>"
        for row in results
    )
    structure_html = "\n".join(
        f"<li>{html.escape(item)}</li>" for item in payload["recommendation"]["securitySkillStructure"]
    )
    rationale_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in payload["recommendation"]["rationale"])
    data_json = html.escape(json.dumps(payload, ensure_ascii=True))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SecureAI Skill Format Benchmark</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #5b6572;
      --line: #d7dde5;
      --panel: #f7f9fb;
      --green: #12805c;
      --blue: #2764c5;
      --red: #bd3b3b;
      --amber: #a66100;
      --teal: #08788c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    header {{
      padding: 24px 28px 16px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); margin: 0; line-height: 1.5; }}
    main {{ padding: 22px 28px 36px; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      background: var(--panel);
      min-height: 92px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin-bottom: 8px;
    }}
    .metric strong {{
      display: block;
      font-size: 22px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, .8fr);
      gap: 22px;
      align-items: start;
    }}
    section {{
      margin-bottom: 24px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 18px;
      background: #fff;
    }}
    .chart-title {{
      font-size: 16px;
      font-weight: 700;
      fill: var(--ink);
    }}
    .axis-label, .value-label {{
      font-size: 13px;
      fill: var(--muted);
    }}
    .bar-0 {{ fill: var(--green); }}
    .bar-1 {{ fill: var(--blue); }}
    .bar-2 {{ fill: var(--amber); }}
    .bar-3 {{ fill: var(--teal); }}
    .bar-4 {{ fill: var(--red); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
      background: var(--panel);
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.55;
    }}
    .note {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 920px) {{
      .summary, .layout {{ grid-template-columns: 1fr; }}
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .panel {{ overflow-x: auto; }}
    }}
  </style>
</head>
<body>
        <header>
        <h1>Skill Format Benchmark: detect-secrets</h1>
        <p>Generated {html.escape(payload['generatedAt'])}.</p>
    </header>
  <main>
    <div class="summary">
            <div class="metric">
                <span>Best structure</span>
                <strong>{html.escape(best['label'])}</strong>
            </div>
            <div class="metric">
                <span>Fastest runtime</span>
                <strong>{html.escape(fastest_row['format'])} {fastest_row['totalMs']} ms</strong>
            </div>
            <div class="metric">
                <span>Smallest package</span>
                <strong>{html.escape(smallest_row['format'])} {smallest_row['bytes']:,} bytes</strong>
            </div>
            <div class="metric">
                <span>Fixture recall</span>
                <strong>{best['signalsPresent']}/{best['expectedSignals']} signals</strong>
            </div>
    </div>
    <div class="layout">
      <div>
        <section class="panel">
          {svg_bar_chart(fastest, 'totalMs', 'Mean Total Runtime by Format', ' ms')}
          <p class="note">Runtime includes parsing, compiling patterns, and scanning targets.</p>
        </section>
        <section class="panel">
          {svg_bar_chart(smallest, 'bytes', 'Serialized Skill Size by Format', ' bytes')}
        </section>
        <section class="panel">
          <h2>Benchmark Table</h2>
          <table>
            <thead>
                            <tr>
                                <th>Format</th>
                                <th>Bytes</th>
                                <th>Parse ms</th>
                                <th>Compile ms</th>
                                <th>Scan ms</th>
                                <th>Total ms</th>
                                <th>Findings</th>
                                <th>Signals</th>
                            </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </section>
      </div>
      <aside>
        <section class="panel">
          <h2>Best Structure</h2>
          <ul>{structure_html}</ul>
        </section>
        <section class="panel">
          <h2>Recommendation</h2>
          <ul>{rationale_html}</ul>
        </section>
      </aside>
    </div>
  </main>
  <script type="application/json" id="benchmark-data">{data_json}</script>
</body>
</html>
"""


def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    skill = load_canonical_skill()
    packaged = package_skills(skill)

    for item in packaged:
        (RESULTS_ROOT / item.file_name).write_text(item.text, encoding="utf-8")

    expected = json.loads(read_text(EXPECTED_FINDINGS))["detect-secrets"]
    targets = expected["targets"]
    signals = expected["signals"]
    results = [benchmark_format(item, targets, signals, rounds=7) for item in packaged]
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "benchmark": "detect-secrets skill format packaging",
        "targets": targets,
        "formats": [item.extension for item in packaged],
        "results": results,
        "recommendation": recommendation(results),
    }

    (RESULTS_ROOT / "skill-format-benchmark.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    (RESULTS_ROOT / "index.html").write_text(render_dashboard(payload), encoding="utf-8")

    best = next(row for row in payload["recommendation"]["ranked"] if row["format"] == "MD")
    print(f"Benchmarked {len(results)} detect-secrets skill formats.")
    print(f"Best structure: {best['label']} ({best['fileName']})")
    print(f"Dashboard: {RESULTS_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
