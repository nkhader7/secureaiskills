from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from agents.ingest import ingest_bytes


def test_ingest_markdown_skill() -> None:
    payload = b"---\nname: demo\ndescription: Demo skill\ntriggers:\n  - /demo\nreferences: {}\n---\n\n# demo\n"
    result = ingest_bytes("SKILL.md", payload)
    assert result.skills_dir.exists()
    assert any(path.endswith("SKILL.md") for path in result.files)


def test_zip_path_traversal_blocked() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../escape.md", "bad")
    with pytest.raises(ValueError):
        ingest_bytes("bad.zip", buf.getvalue())


def test_unsupported_extension_blocked() -> None:
    with pytest.raises(ValueError):
        ingest_bytes("malware.exe", b"nope")
