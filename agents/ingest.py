"""Upload and repository ingestion helpers with safe archive extraction."""
from __future__ import annotations

import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = REPO_ROOT / "output" / "uploads"

ALLOWED_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".toml", ".json", ".py", ".txt", ".cfg", ".ini", ".xml", ".zip",
}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 1000


@dataclass
class IngestedSkill:
    upload_id: str
    workspace: Path
    skills_dir: Path
    files: list[str]
    warnings: list[str]


def _ensure_inside(base: Path, target: Path) -> None:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    if base_resolved != target_resolved and base_resolved not in target_resolved.parents:
        raise ValueError(f"Unsafe path traversal blocked: {target}")


def _validate_name(name: str) -> None:
    suffix = Path(name).suffix.lower()
    if suffix and suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {suffix}")


def create_workspace() -> Path:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    workspace = UPLOAD_ROOT / uuid.uuid4().hex
    workspace.mkdir(parents=True)
    return workspace


def ingest_bytes(filename: str, data: bytes) -> IngestedSkill:
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Upload exceeds {MAX_UPLOAD_BYTES} bytes")
    _validate_name(filename)
    workspace = create_workspace()
    raw_path = workspace / "raw" / Path(filename).name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(data)

    warnings: list[str] = []
    if raw_path.suffix.lower() == ".zip":
        extract_dir = workspace / "extracted"
        _safe_extract_zip(raw_path, extract_dir)
        skills_dir = _detect_skills_dir(extract_dir, warnings)
    else:
        skills_dir = workspace / "skills"
        skill_dir = skills_dir / _safe_skill_name(raw_path.stem)
        skill_dir.mkdir(parents=True, exist_ok=True)
        if raw_path.name.upper() == "SKILL.MD" or raw_path.suffix.lower() == ".md":
            shutil.copy2(raw_path, skill_dir / "SKILL.md")
        else:
            shutil.copy2(raw_path, skill_dir / raw_path.name)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_dir.name}\ndescription: Uploaded skill artifact\ntriggers:\n  - /{skill_dir.name}\nreferences: {{}}\n---\n\n"
                f"# {skill_dir.name}\n\nUploaded artifact `{raw_path.name}` for analysis.\n",
                encoding="utf-8",
            )
            warnings.append("Non-Markdown upload wrapped in a generated SKILL.md for structural analysis.")

    files = [str(p.relative_to(workspace)) for p in workspace.rglob("*") if p.is_file()]
    return IngestedSkill(workspace.name, workspace, skills_dir, files, warnings)


def ingest_path(path: Path) -> IngestedSkill:
    if not path.exists():
        raise ValueError(f"Path not found: {path}")
    workspace = create_workspace()
    warnings: list[str] = []
    if path.is_dir():
        dest = workspace / "repository"
        shutil.copytree(path, dest)
        skills_dir = _detect_skills_dir(dest, warnings)
    else:
        return ingest_bytes(path.name, path.read_bytes())
    files = [str(p.relative_to(workspace)) for p in workspace.rglob("*") if p.is_file()]
    return IngestedSkill(workspace.name, workspace, skills_dir, files, warnings)


def _safe_extract_zip(zip_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    total = 0
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_ARCHIVE_MEMBERS:
            raise ValueError(f"Archive contains more than {MAX_ARCHIVE_MEMBERS} files")
        for info in infos:
            if info.is_dir():
                continue
            _validate_name(info.filename)
            total += info.file_size
            if total > MAX_UPLOAD_BYTES:
                raise ValueError(f"Archive uncompressed size exceeds {MAX_UPLOAD_BYTES} bytes")
            target = dest / info.filename
            _ensure_inside(dest, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out)


def _detect_skills_dir(root: Path, warnings: list[str]) -> Path:
    candidates = [root / "skills", root]
    for candidate in candidates:
        if candidate.exists() and any((p / "SKILL.md").exists() for p in candidate.iterdir() if p.is_dir()):
            return candidate
    skill_files = list(root.rglob("SKILL.md"))
    if skill_files:
        parent = skill_files[0].parent.parent
        warnings.append(f"Detected nested skill collection at {parent.relative_to(root)}")
        return parent
    generated = root / "skills" / "uploaded-skill"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "SKILL.md").write_text(
        "---\nname: uploaded-skill\ndescription: Uploaded repository artifact\ntriggers:\n  - /uploaded-skill\nreferences: {}\n---\n\n"
        "# uploaded-skill\n\nRepository uploaded for broad framework analysis.\n",
        encoding="utf-8",
    )
    warnings.append("No SKILL.md found; generated uploaded-skill/SKILL.md wrapper.")
    return root / "skills"


def _safe_skill_name(name: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    return cleaned or "uploaded-skill"
