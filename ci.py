"""CI/CD runner - executes validation checks and exits non-zero on failure."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from agents.orchestrator import run_all, DEFAULT_OUTPUT_DIR
from agents.schemas import Thresholds, apply_thresholds


def main() -> int:
    parser = argparse.ArgumentParser(description="SecureAI Skills CI runner")
    parser.add_argument("--skills-dir", default="skills")
    parser.add_argument("--skill", action="append", default=[], metavar="SKILL")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--minimum-security-score", type=int, default=80)
    parser.add_argument("--minimum-compliance-score", type=int, default=80)
    parser.add_argument("--minimum-validation-score", type=int, default=80)
    parser.add_argument("--minimum-benchmark-score", type=int, default=70)
    args = parser.parse_args()

    report = asyncio.run(run_all(args.skills_dir, args.skill or None, args.output_dir))
    thresholds = Thresholds(
        minimum_security_score=args.minimum_security_score,
        minimum_compliance_score=args.minimum_compliance_score,
        minimum_validation_score=args.minimum_validation_score,
        minimum_benchmark_score=args.minimum_benchmark_score,
    )
    gate = apply_thresholds(report, thresholds)
    summary = {
        "decision": gate["decision"],
        "failure_reasons": gate["failure_reasons"],
        "overall_risk": report["overall_risk"],
        "skills_analyzed": report["skills_analyzed"],
        "confidence": report["confidence"],
        "security_score": gate["security_score"],
        "compliance_score": gate["compliance_score"],
        "validation_score": gate["validation_score"],
        "benchmark_score": gate["benchmark_score"],
        "overall_score": gate["overall_score"],
        "output": args.output_dir,
    }
    print(json.dumps(summary, indent=2))
    return 0 if gate["decision"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
