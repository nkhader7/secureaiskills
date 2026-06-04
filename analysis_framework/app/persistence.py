"""SQLite persistence layer for skill analysis reports."""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

DB_PATH = os.getenv("SKILL_ANALYSIS_DB", "analysis_framework/reports.db")


class ReportDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.ensure_schema()

    def get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def ensure_schema(self):
        """Ensure database schema exists."""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                skill_id TEXT,
                timestamp TEXT,
                summary_json TEXT,
                agent1_json TEXT,
                agent2_json TEXT,
                agent3_json TEXT,
                security_score REAL,
                compliance_score REAL,
                validation_score REAL,
                overall_score REAL,
                pass_fail TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_report(self, report_id: str, skill_id: str, report: Dict[str, Any]) -> bool:
        """Save report to database."""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO reports
                (id, skill_id, timestamp, summary_json, agent1_json, agent2_json, agent3_json,
                 security_score, compliance_score, validation_score, overall_score, pass_fail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                skill_id,
                datetime.utcnow().isoformat(),
                json.dumps(report.get('summary', {})),
                json.dumps(report.get('agent1', {})),
                json.dumps(report.get('agent2', {})),
                json.dumps(report.get('agent3', {})),
                report.get('security_score', 0.0),
                report.get('compliance_score', 0.0),
                report.get('validation_score', 0.0),
                report.get('overall_score', 0.0),
                report.get('pass_fail', 'unknown'),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
        finally:
            conn.close()

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve report from database."""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'skill_id': row[1],
                'timestamp': row[2],
                'summary': json.loads(row[3]),
                'agent1': json.loads(row[4]),
                'agent2': json.loads(row[5]),
                'agent3': json.loads(row[6]),
                'security_score': row[7],
                'compliance_score': row[8],
                'validation_score': row[9],
                'overall_score': row[10],
                'pass_fail': row[11],
            }
        finally:
            conn.close()

    def list_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent reports."""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, skill_id, timestamp, security_score, overall_score, pass_fail FROM reports ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': r[0],
                    'skill_id': r[1],
                    'timestamp': r[2],
                    'security_score': r[3],
                    'overall_score': r[4],
                    'pass_fail': r[5],
                }
                for r in rows
            ]
        finally:
            conn.close()

    def delete_report(self, report_id: str) -> bool:
        """Delete a report."""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting report: {e}")
            return False
        finally:
            conn.close()


# Singleton instance
_db_instance: Optional[ReportDB] = None


def get_db() -> ReportDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = ReportDB()
    return _db_instance
