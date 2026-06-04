import os
import zipfile
import tempfile
import shutil
import base64
from typing import Dict

DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50 MB per file limit
ALLOWED_EXTS = {'.py', '.md', '.yaml', '.yml', '.json', '.toml', '.txt', '.cfg', '.ini'}

def _is_within_directory(directory: str, target: str) -> bool:
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return abs_target.startswith(abs_directory + os.sep)

def safe_extract_zip(zip_path: str, dest_dir: str, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            # Prevent path traversal
            member_path = os.path.join(dest_dir, member.filename)
            if not _is_within_directory(dest_dir, member_path):
                raise RuntimeError(f"Illegal zip member path: {member.filename}")
            # Prevent zip bombs by limiting extracted size
            if member.file_size > max_bytes:
                raise RuntimeError(f"File {member.filename} exceeds allowed size")
        zf.extractall(dest_dir)

def build_files_index_from_dir(root_dir: str, max_bytes: int = DEFAULT_MAX_BYTES) -> Dict[str, str]:
    files = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root_dir)
            ext = os.path.splitext(fname)[1].lower()
            if os.path.getsize(full) > max_bytes:
                files[rel] = f"__SKIPPED_TOO_LARGE__ ({os.path.getsize(full)} bytes)"
                continue
            try:
                if ext in ALLOWED_EXTS:
                    with open(full, 'r', encoding='utf-8', errors='replace') as fh:
                        files[rel] = fh.read()
                else:
                    # Binary or unknown files -> base64 encode
                    with open(full, 'rb') as fh:
                        files[rel] = "__BASE64__:" + base64.b64encode(fh.read()).decode('ascii')
            except Exception as e:
                files[rel] = f"__ERROR_READING__: {str(e)}"
    return files

def process_uploaded_zip_bytes(data_stream, max_bytes: int = DEFAULT_MAX_BYTES) -> Dict[str, str]:
    tmpdir = tempfile.mkdtemp(prefix='skill-upload-')
    try:
        zpath = os.path.join(tmpdir, 'upload.zip')
        with open(zpath, 'wb') as out:
            shutil.copyfileobj(data_stream, out)
        safe_extract_zip(zpath, tmpdir, max_bytes=max_bytes)
        files = build_files_index_from_dir(tmpdir, max_bytes=max_bytes)
        return files
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
