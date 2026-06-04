"""Shared response schemas and CI threshold helpers."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Thresholds(BaseModel):
    fail_on_critical: bool = True
    fail_on_high: bool = True
    minimum_security_score: int = 80
    minimum_compliance_score: int = 80
    minimum_validation_score: int = 80
    minimum_benchmark_score: int = 70


class AnalyzeRequest(BaseModel):
    skills_dir: str = "skills"
    skills: list[str] = Field(default_factory=list)
    thresholds: Thresholds = Field(default_factory=Thresholds)


class UploadAnalyzeResponse(BaseModel):
    upload_id: str
    skills_dir: str
    files: list[str]
    warnings: list[str]
    report: dict[str, Any]


def score_summary(report: dict[str, Any]) -> dict[str, float]:
    security = 100.0 if report.get("overall_risk") == "low" else 75.0 if report.get("overall_risk") == "medium" else 50.0
    compliance_rows = report.get("compliance_report") or []
    compliance = 100.0
    if compliance_rows:
        valid = sum(1 for row in compliance_rows if row.get("governance_valid", True))
        compliance = round(valid / max(len(compliance_rows), 1) * 100, 1)
    ci_rows = report.get("ci_cd_report") or []
    validation = round(sum(row.get("validation_score", 0) for row in ci_rows) / max(len(ci_rows), 1), 1) if ci_rows else 0.0
    bench_rows = report.get("benchmark_report") or []
    benchmark = round(sum(row.get("benchmark_score", 0) for row in bench_rows) / max(len(bench_rows), 1) * 10, 1) if bench_rows else 0.0
    coverage = round((report.get("coverage_map") or {}).get("coverage_score", 0) * 100, 1)
    overall = round((security + compliance + validation + benchmark + coverage) / 5, 1)
    return {
        "security_score": security,
        "compliance_score": compliance,
        "validation_score": validation,
        "coverage_score": coverage,
        "benchmark_score": benchmark,
        "overall_score": overall,
    }


def apply_thresholds(report: dict[str, Any], thresholds: Thresholds) -> dict[str, Any]:
    scores = score_summary(report)
    reasons: list[str] = []
    if scores["security_score"] < thresholds.minimum_security_score:
        reasons.append("security_score below threshold")
    if scores["compliance_score"] < thresholds.minimum_compliance_score:
        reasons.append("compliance_score below threshold")
    if scores["validation_score"] < thresholds.minimum_validation_score:
        reasons.append("validation_score below threshold")
    if scores["benchmark_score"] < thresholds.minimum_benchmark_score:
        reasons.append("benchmark_score below threshold")
    decision = "fail" if reasons or report.get("pass_fail_decision") == "fail" else "pass"
    return {"decision": decision, "failure_reasons": reasons, **scores}
