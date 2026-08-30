"""SQLite database management for X-ONE"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.models import ChatMessage, Finding


class XoneMemory:
    """Manages chat history and session memory"""

    def __init__(self, db_path: Path = Path("xone_memory.db")):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT
            )
        """)

        # Findings table (moved to FindingsDB)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                vuln_type TEXT NOT NULL,
                url TEXT NOT NULL,
                payload TEXT NOT NULL,
                severity TEXT NOT NULL,
                param TEXT,
                context TEXT NOT NULL,
                evidence TEXT,
                tool TEXT NOT NULL,
                cvss_score REAL,
                cvss_vector TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON findings(severity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool ON findings(tool)")

        conn.commit()
        conn.close()

    def save_message(self, session_id: str, message: ChatMessage) -> bool:
        """Save message to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, role, content, model, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, message.role, message.content, message.model, message.timestamp))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Error] Failed to save message: {e}")
            return False

    def get_history(self, session_id: str, limit: int = 20) -> list[ChatMessage]:
        """Get chat history for session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, model, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            conn.close()

            messages = []
            for role, content, model, timestamp in reversed(rows):
                msg = ChatMessage(
                    role=role,
                    content=content,
                    model=model,
                    timestamp=datetime.fromisoformat(timestamp)
                )
                messages.append(msg)
            return messages
        except Exception as e:
            print(f"[Error] Failed to get history: {e}")
            return []

    def clear_session(self, session_id: str) -> bool:
        """Clear all messages in a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Error] Failed to clear session: {e}")
            return False

    def list_sessions(self, limit: int = 10) -> list[dict]:
        """List recent sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, created_at, last_activity, title,
                       (SELECT COUNT(*) FROM chat_history WHERE session_id = sessions.session_id) as msg_count
                FROM sessions
                ORDER BY last_activity DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()

            sessions = []
            for sid, created, last, title, count in rows:
                sessions.append({
                    "session_id": sid,
                    "created_at": created,
                    "last_activity": last,
                    "title": title or "Untitled",
                    "message_count": count
                })
            return sessions
        except Exception as e:
            print(f"[Error] Failed to list sessions: {e}")
            return []


class FindingsDB:
    """Manages security findings storage"""

    def __init__(self, db_path: Path = Path("xone_memory.db")):
        self.db_path = db_path
        self.json_path = Path("findings.json")

    def add(self, finding: Finding) -> bool:
        """Add finding to database and JSON backup"""
        try:
            # SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO findings (id, vuln_type, url, payload, severity, param, context, evidence, tool, cvss_score, cvss_vector, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                finding.id, finding.vuln_type, finding.url, finding.payload,
                finding.severity, finding.param, finding.context, finding.evidence,
                finding.tool, finding.cvss_score, finding.cvss_vector, finding.timestamp
            ))
            conn.commit()
            conn.close()

            # JSON backup
            self._backup_to_json()
            return True
        except Exception as e:
            print(f"[Error] Failed to add finding: {e}")
            return False

    def get_all(self) -> list[Finding]:
        """Get all findings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM findings ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()

            findings = []
            for row in rows:
                finding = Finding(
                    id=row[0],
                    vuln_type=row[1],
                    url=row[2],
                    payload=row[3],
                    severity=row[4],
                    param=row[5],
                    context=row[6],
                    evidence=row[7],
                    tool=row[8],
                    cvss_score=row[9],
                    cvss_vector=row[10],
                    timestamp=datetime.fromisoformat(row[11])
                )
                findings.append(finding)
            return findings
        except Exception as e:
            print(f"[Error] Failed to get findings: {e}")
            return []

    def by_severity(self, severity: str) -> list[Finding]:
        """Get findings by severity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM findings WHERE severity = ? ORDER BY timestamp DESC",
                (severity,)
            )
            rows = cursor.fetchall()
            conn.close()

            findings = []
            for row in rows:
                finding = Finding(
                    id=row[0], vuln_type=row[1], url=row[2], payload=row[3],
                    severity=row[4], param=row[5], context=row[6], evidence=row[7],
                    tool=row[8], cvss_score=row[9], cvss_vector=row[10],
                    timestamp=datetime.fromisoformat(row[11])
                )
                findings.append(finding)
            return findings
        except Exception as e:
            print(f"[Error] Failed to get findings by severity: {e}")
            return []

    def delete_all(self) -> bool:
        """Delete all findings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM findings")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Error] Failed to delete findings: {e}")
            return False

    def export_json(self) -> str:
        """Export findings as JSON"""
        findings = self.get_all()
        return json.dumps(
            [f.model_dump(mode='json') for f in findings],
            indent=2,
            default=str
        )

    def _backup_to_json(self):
        """Backup findings to JSON file"""
        try:
            with open(self.json_path, 'w') as f:
                f.write(self.export_json())
        except Exception as e:
            print(f"[Warning] Failed to backup to JSON: {e}")

    def get_summary(self) -> dict:
        """Get findings summary"""
        findings = self.get_all()
        summary = {
            "total": len(findings),
            "by_severity": {
                "Critical": len([f for f in findings if f.severity == "Critical"]),
                "High": len([f for f in findings if f.severity == "High"]),
                "Medium": len([f for f in findings if f.severity == "Medium"]),
                "Low": len([f for f in findings if f.severity == "Low"]),
                "Info": len([f for f in findings if f.severity == "Info"]),
            },
            "by_type": {},
        }
        for finding in findings:
            if finding.vuln_type not in summary["by_type"]:
                summary["by_type"][finding.vuln_type] = 0
            summary["by_type"][finding.vuln_type] += 1
        return summary
