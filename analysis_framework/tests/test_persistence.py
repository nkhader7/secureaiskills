"""Tests for persistence module."""
import sys
import os
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from analysis_framework.app.persistence import ReportDB


def test_report_db_create_and_retrieve():
    """Test creating and retrieving a report."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    
    db = ReportDB(db_path)
    
    # Save a report
    report_id = "test-report-1"
    skill_id = "test-skill"
    report = {
        "summary": {"name": "TestSkill"},
        "security_score": 85.0,
        "compliance_score": 90.0,
        "validation_score": 80.0,
        "overall_score": 85.0,
        "pass_fail": "pass",
    }
    
    result = db.save_report(report_id, skill_id, report)
    assert result is True
    
    # Retrieve the report
    retrieved = db.get_report(report_id)
    assert retrieved is not None
    assert retrieved["id"] == report_id
    assert retrieved["skill_id"] == skill_id
    assert retrieved["security_score"] == 85.0
    assert retrieved["pass_fail"] == "pass"


def test_report_db_list_reports():
    """Test listing reports."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    
    db = ReportDB(db_path)
    
    # Save multiple reports
    for i in range(3):
        report_id = f"test-report-{i}"
        skill_id = f"test-skill-{i}"
        report = {
            "summary": {"name": f"TestSkill{i}"},
            "security_score": 70.0 + i * 5,
            "compliance_score": 80.0,
            "validation_score": 85.0,
            "overall_score": 78.0,
            "pass_fail": "pass",
        }
        db.save_report(report_id, skill_id, report)
    
    # List reports
    reports = db.list_reports(limit=10)
    assert len(reports) >= 3


def test_report_db_delete_report():
    """Test deleting a report."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    
    db = ReportDB(db_path)
    
    # Save a report
    report_id = "test-report-delete"
    db.save_report(report_id, "test-skill", {"summary": {}})
    
    # Verify it exists
    retrieved = db.get_report(report_id)
    assert retrieved is not None
    
    # Delete it
    result = db.delete_report(report_id)
    assert result is True
    
    # Verify it's gone
    retrieved = db.get_report(report_id)
    assert retrieved is None
