from __future__ import annotations

import asyncio
import json
from pathlib import Path

from agent3 import DEFAULT_OUTPUT_DIR, run_agent3


def main() -> int:
    report = asyncio.run(run_agent3(output_dir=str(DEFAULT_OUTPUT_DIR)))
    ci_path = Path(DEFAULT_OUTPUT_DIR) / "ci" / "agent3-ci-output.json"
    print(json.dumps({"decision": report["pass_fail_decision"], "ci_output": str(ci_path)}, indent=2))
    return 0 if report["pass_fail_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
