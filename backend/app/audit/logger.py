import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn():
    conn = sqlite3.connect(settings.SQLITE_AUDIT_DB)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    import os
    os.makedirs(os.path.dirname(settings.SQLITE_AUDIT_DB), exist_ok=True)
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                execution_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                status TEXT NOT NULL,
                pending_action TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_exec ON audit_events(execution_id)")


def log_event(execution_id: str, tenant_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO audit_events (execution_id, tenant_id, event_type, payload, timestamp) VALUES (?, ?, ?, ?, ?)",
            (execution_id, tenant_id, event_type, json.dumps(payload, default=str), _now()),
        )


def create_execution(execution_id: str, tenant_id: str, status: str, pending_action: Optional[Dict[str, Any]] = None) -> None:
    now = _now()
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO executions (execution_id, tenant_id, status, pending_action, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (execution_id, tenant_id, status, json.dumps(pending_action, default=str) if pending_action else None, now, now),
        )


def update_execution_status(execution_id: str, status: str, pending_action: Optional[Dict[str, Any]] = None) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE executions SET status = ?, pending_action = ?, updated_at = ? WHERE execution_id = ?",
            (status, json.dumps(pending_action, default=str) if pending_action else None, _now(), execution_id),
        )


def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute("SELECT execution_id, tenant_id, status, pending_action FROM executions WHERE execution_id = ?", (execution_id,))
        row = cur.fetchone()
        if not row:
            return None
        events_cur = conn.execute(
            "SELECT execution_id, tenant_id, event_type, payload, timestamp FROM audit_events WHERE execution_id = ? ORDER BY id ASC",
            (execution_id,),
        )
        events = [
            {
                "execution_id": r[0],
                "tenant_id": r[1],
                "event_type": r[2],
                "payload": json.loads(r[3]),
                "timestamp": r[4],
            }
            for r in events_cur.fetchall()
        ]
        return {
            "execution_id": row[0],
            "tenant_id": row[1],
            "status": row[2],
            "pending_action": json.loads(row[3]) if row[3] else None,
            "events": events,
        }


def list_executions(tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT execution_id, tenant_id, status, created_at FROM executions WHERE tenant_id = ? ORDER BY created_at DESC LIMIT ?",
            (tenant_id, limit),
        )
        return [
            {"execution_id": r[0], "tenant_id": r[1], "status": r[2], "created_at": r[3]}
            for r in cur.fetchall()
        ]