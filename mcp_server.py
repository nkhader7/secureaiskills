#!/usr/bin/env python3
"""
SecureAI Skills MCP Server
Serves 21 security analysis skills as MCP tools at http://127.0.0.1:8765/mcp

Usage:
    pip install -r requirements.txt
    python mcp_server.py
"""

from pathlib import Path
import re
import time

try:
    import yaml as _yaml

    def _parse_yaml(text: str) -> dict:
        return _yaml.safe_load(text) or {}

except ImportError:

    def _parse_yaml(text: str) -> dict:
        return {}


from mcp.server.fastmcp import FastMCP

SKILLS_DIR = Path(__file__).parent / "skills"

mcp = FastMCP(
    "secureai-skills",
    instructions=(
        "SecureAI Skills provides 21 LLM-driven security analysis skills covering "
        "OWASP Top 10, ASVS 5.0, supply chain risks, secrets detection, IaC security, "
        "and more. Each tool returns skill instructions + rules that you then execute "
        "by reading the target files and applying the embedded rule set."
    ),
    host="127.0.0.1",
    port=8765,
    # streamable_http_path defaults to "/mcp" → serves at http://127.0.0.1:8765/mcp
)

# ── Helpers ────────────────────────────────────────────────────────────────────


def _skill_dirs() -> list[Path]:
    return sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("_"))


def _parse_skill_md(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.+?)\n---\n(.+)$", content, re.DOTALL)
    if not m:
        return {}, content.strip()
    return _parse_yaml(m.group(1)), m.group(2).strip()


def _count_rules(rules_text: str) -> int:
    return len(re.findall(r"^\s*-\s+id:", rules_text, re.MULTILINE))


def _est_tokens(text: str) -> int:
    # Rough GPT/Claude estimate: ~4 chars per token
    return max(1, len(text) // 4)


def _load_skill(skill_name: str) -> dict | None:
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    t0 = time.perf_counter()
    fm, body = _parse_skill_md(skill_md)

    rules_path = skill_dir / "references" / "rules.yaml"
    rules_raw = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    load_ms = (time.perf_counter() - t0) * 1000

    truncated = len(rules_raw) > 60_000
    rules = (
        rules_raw[:60_000] + "\n# ... (truncated — load full file from disk for exhaustive scan)"
        if truncated
        else rules_raw
    )

    return {
        "name": skill_name,
        "description": fm.get("description", ""),
        "triggers": fm.get("triggers", []),
        "body": body,
        "rules": rules,
        # perf metadata
        "_rule_count": _count_rules(rules_raw),
        "_rules_bytes": len(rules_raw),
        "_load_ms": load_ms,
        "_truncated": truncated,
    }


def _assemble(skill: dict, target: str, flags: str) -> str:
    t0 = time.perf_counter()

    parts = [skill["body"]]
    if target:
        parts.append(f"\n---\n**Target:** `{target}`")
    if flags:
        parts.append(f"**Flags:** `{flags}`")
    if skill["rules"]:
        parts.append(f"\n---\n## Rules (rules.yaml)\n\n```yaml\n{skill['rules']}\n```")

    body = "\n".join(parts)
    assemble_ms = (time.perf_counter() - t0) * 1000
    total_ms = skill["_load_ms"] + assemble_ms

    rule_count = skill["_rule_count"]
    rules_kb = skill["_rules_bytes"] / 1024
    output_tokens = _est_tokens(body)
    truncated_note = " (truncated at 60 KB)" if skill["_truncated"] else ""

    perf = (
        f"\n\n---\n"
        f"**Performance**\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Skill loaded | `{skill['_load_ms']:.1f} ms` |\n"
        f"| Response assembled | `{assemble_ms:.1f} ms` |\n"
        f"| Total latency | `{total_ms:.1f} ms` |\n"
        f"| Rules loaded | `{rule_count}` |\n"
        f"| Rules file size | `{rules_kb:.1f} KB`{truncated_note} |\n"
        f"| Est. output tokens | `~{output_tokens:,}` |\n"
    )

    return body + perf


# ── Dynamic skill tool registration ───────────────────────────────────────────


def _register_skills() -> None:
    for skill_dir in _skill_dirs():
        skill_name = skill_dir.name
        skill = _load_skill(skill_name)
        if not skill:
            continue

        description = skill["description"] or f"Run {skill_name} security analysis"

        def _make_fn(sname: str):
            def tool_fn(target: str = "", flags: str = "") -> str:
                t_invoke = time.perf_counter()
                sk = _load_skill(sname)
                if not sk:
                    return f"Skill '{sname}' not found in {SKILLS_DIR}"
                result = _assemble(sk, target, flags)
                invoke_ms = (time.perf_counter() - t_invoke) * 1000
                return result + f"| MCP tool invoke | `{invoke_ms:.1f} ms` |\n"

            tool_fn.__name__ = sname.replace("-", "_")
            return tool_fn

        mcp.tool(name=skill_name, description=description)(_make_fn(skill_name))


_register_skills()


# ── Dynamic skill prompt registration (slash commands) ────────────────────────


def _register_prompts() -> None:
    for skill_dir in _skill_dirs():
        skill_name = skill_dir.name
        skill = _load_skill(skill_name)
        if not skill:
            continue

        description = skill["description"] or f"Run {skill_name} security analysis"

        def _make_prompt_fn(sname: str):
            def prompt_fn(target: str = "", flags: str = "") -> str:
                sk = _load_skill(sname)
                if not sk:
                    return f"Skill '{sname}' not found."
                return _assemble(sk, target, flags)

            prompt_fn.__name__ = sname.replace("-", "_") + "_prompt"
            return prompt_fn

        mcp.prompt(name=skill_name, description=description)(_make_prompt_fn(skill_name))


_register_prompts()


# ── Utility tool ───────────────────────────────────────────────────────────────


@mcp.tool(
    name="list-skills",
    description="List all available SecureAI security skills with their descriptions and trigger commands",
)
def list_skills() -> str:
    lines = ["# SecureAI Skills\n"]
    for skill_dir in _skill_dirs():
        sk = _load_skill(skill_dir.name)
        if sk:
            triggers = ", ".join(sk["triggers"][:2]) if sk["triggers"] else ""
            trigger_note = f"  (triggers: `{triggers}`)" if triggers else ""
            lines.append(f"- **{sk['name']}**: {sk['description']}{trigger_note}")
    lines.append(f"\n_Total: {len(_skill_dirs())} skills_")
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting SecureAI Skills MCP server at http://127.0.0.1:8765/mcp")
    mcp.run(transport="streamable-http")
