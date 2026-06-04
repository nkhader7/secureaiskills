from __future__ import annotations

from agents.schemas import Thresholds, apply_thresholds


def test_apply_thresholds_passes_good_report() -> None:
    report = {
        "overall_risk": "low",
        "pass_fail_decision": "pass",
        "coverage_map": {"coverage_score": 1.0},
        "compliance_report": [{"governance_valid": True}],
        "ci_cd_report": [{"validation_score": 95}],
        "benchmark_report": [{"benchmark_score": 8.5}],
    }
    gate = apply_thresholds(report, Thresholds())
    assert gate["decision"] == "pass"
    assert gate["overall_score"] >= 80


def test_apply_thresholds_fails_low_validation() -> None:
    report = {
        "overall_risk": "low",
        "pass_fail_decision": "pass",
        "coverage_map": {"coverage_score": 1.0},
        "compliance_report": [{"governance_valid": True}],
        "ci_cd_report": [{"validation_score": 40}],
        "benchmark_report": [{"benchmark_score": 8.5}],
    }
    gate = apply_thresholds(report, Thresholds())
    assert gate["decision"] == "fail"
    assert "validation_score below threshold" in gate["failure_reasons"]
