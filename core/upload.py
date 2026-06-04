"""
Upload façade — thin wrapper around agents.ingest for use in Streamlit pages
and the FastAPI /analyze/upload endpoint.
"""
from __future__ import annotations

from typing import Any

from agents.ingest import IngestedSkill, ingest_bytes, ingest_path

__all__ = ["IngestedSkill", "ingest_bytes", "ingest_path", "summarise_ingested"]


def summarise_ingested(result: IngestedSkill) -> dict[str, Any]:
    """Return a human-readable summary dict of an ingested skill workspace."""
    return {
        "upload_id": result.upload_id,
        "skills_dir": str(result.skills_dir),
        "file_count": len(result.files),
        "files": result.files[:50],
        "warnings": result.warnings,
    }
