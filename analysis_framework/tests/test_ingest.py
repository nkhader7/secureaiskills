"""Tests for ingest module."""
import sys
import os
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from analysis_framework.app.ingest import (
    safe_extract_zip,
    build_files_index_from_dir,
    _is_within_directory,
)


def test_is_within_directory_safe():
    """Test path traversal protection."""
    tmpdir = tempfile.mkdtemp()
    safe_path = os.path.join(tmpdir, "safe_file.txt")
    assert _is_within_directory(tmpdir, safe_path)


def test_is_within_directory_traversal_attack():
    """Test path traversal attack detection."""
    tmpdir = tempfile.mkdtemp()
    parent = os.path.dirname(tmpdir)
    traversal_path = os.path.join(tmpdir, "..", "..", "etc", "passwd")
    assert not _is_within_directory(tmpdir, traversal_path)


def test_safe_extract_zip_basic():
    """Test basic ZIP extraction."""
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, "test.zip")
    extract_dir = os.path.join(tmpdir, "extracted")
    os.makedirs(extract_dir)
    
    # Create a simple ZIP file
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test.txt", "Hello World")
        zf.writestr("subdir/file.md", "# Test")
    
    # Extract and verify
    safe_extract_zip(zip_path, extract_dir)
    assert os.path.exists(os.path.join(extract_dir, "test.txt"))
    assert os.path.exists(os.path.join(extract_dir, "subdir", "file.md"))


def test_build_files_index_from_dir():
    """Test directory indexing."""
    tmpdir = tempfile.mkdtemp()
    
    # Create test files
    with open(os.path.join(tmpdir, "test.md"), "w") as f:
        f.write("# Hello")
    with open(os.path.join(tmpdir, "test.py"), "w") as f:
        f.write("print('hello')")
    
    files_index = build_files_index_from_dir(tmpdir)
    
    assert "test.md" in files_index
    assert "test.py" in files_index
    assert "# Hello" in files_index["test.md"]
    assert "print('hello')" in files_index["test.py"]
