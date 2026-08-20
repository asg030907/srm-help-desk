"""
store.py
SQLite-backed ticket store shared by the Intake Agent (creates tickets)
and the Dispatch Agent (reads + assigns them).

This is deliberately not the same thing as `src/agent/memory.py`:
conversation memory is per-session and only the Intake Agent touches
it. Tickets need to survive across two independently-run agents (one
triggered per chat message, one triggered on a timer), so they live in
their own small SQLite database instead.
"""

import sqlite3
import threading
from pathlib import Path

from src.tickets.models import Ticket
from src.utils.helpers import new_id
from src.utils.logger import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    name TEXT,
    regno TEXT,
    hostel TEXT,
    category TEXT,
    description TEXT,
    department TEXT,
    urgency TEXT,
    status TEXT,
    assigned_technician TEXT,
    scheduled_slot TEXT,
    dispatch_note TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""


class TicketStore:
    """
    Thread-safe SQLite ticket store. One instance per process is enough
    — the background scheduler thread (Dispatch Agent) and the FastAPI
    request threads (Intake Agent, via /api/chat) share it under a lock.
    """

    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._lock = threading.Lock()
        with self._connect() as conn:
            conn.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create(
        self,
        *,
        name: str,
        regno: str,
        hostel: str,
        category: str,
        description: str,
        department: str,
        urgency: str,
    ) -> Ticket:
        ticket = Ticket(
            id=new_id("ticket"),
            name=name,
            regno=regno,
            hostel=hostel,
            category=category,
            description=description,
            department=department,
            urgency=urgency,
            status="open",
        )
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO tickets (id, name, regno, hostel, category, description, "
                "department, urgency, status, assigned_technician, scheduled_slot, "
                "dispatch_note, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    ticket.id, ticket.name, ticket.regno, ticket.hostel, ticket.category,
                    ticket.description, ticket.department, ticket.urgency, ticket.status,
                    ticket.assigned_technician, ticket.scheduled_slot, ticket.dispatch_note,
                    ticket.created_at, ticket.updated_at,
                ),
            )
        logger.info("Created ticket %s (%s, urgency=%s)", ticket.id, department, urgency)
        return ticket

    def list_open(self) -> list[Ticket]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE status = 'open' "
                "ORDER BY CASE urgency WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, created_at ASC"
            ).fetchall()
        return [self._row_to_ticket(r) for r in rows]

    def list_all(self) -> list[Ticket]:
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
        return [self._row_to_ticket(r) for r in rows]

    def get(self, ticket_id: str) -> Ticket | None:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return self._row_to_ticket(row) if row else None

    def assign(self, ticket_id: str, technician: str, scheduled_slot: str, note: str = "") -> Ticket | None:
        from datetime import datetime

        now = datetime.utcnow().isoformat()
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE tickets SET status='assigned', assigned_technician=?, "
                "scheduled_slot=?, dispatch_note=?, updated_at=? WHERE id=?",
                (technician, scheduled_slot, note, now, ticket_id),
            )
        logger.info("Assigned ticket %s to %s at %s", ticket_id, technician, scheduled_slot)
        return self.get(ticket_id)

    @staticmethod
    def _row_to_ticket(row: sqlite3.Row) -> Ticket:
        return Ticket(**{key: row[key] for key in row.keys()})


_default_store: TicketStore | None = None


def get_default_ticket_store() -> TicketStore:
    """Process-wide default ticket store, built from settings on first use."""
    global _default_store
    if _default_store is None:
        from src.utils.config import get_settings

        _default_store = TicketStore(get_settings().tickets_db_path)
    return _default_store
