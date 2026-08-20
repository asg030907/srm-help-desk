"""
models.py
Data model for a single help-desk ticket. The Intake Agent creates
these; the Dispatch Agent reads and updates them. Neither agent talks
to the other directly — this row, sitting in shared storage, is the
entire handoff.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Ticket:
    id: str
    name: str
    regno: str
    hostel: str
    category: str
    description: str
    department: str
    urgency: str  # "low" | "medium" | "high"
    status: str = "open"  # "open" | "assigned" | "resolved"
    assigned_technician: str | None = None
    scheduled_slot: str | None = None
    dispatch_note: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
