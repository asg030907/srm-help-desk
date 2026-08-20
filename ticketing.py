"""
ticketing.py
Ticket tools shared by both agents:
  - the Intake Agent calls `create_ticket` to log something it can't
    resolve directly in the conversation.
  - the Dispatch Agent calls `list_open_tickets`, `list_technicians`,
    and `assign_ticket` to run a batch pass over everything open.

Both read/write the same SQLite-backed TicketStore. That shared store
is the entire handoff between the two agents — neither one calls the
other directly.
"""

import re

from crewai.tools import tool

from src.tickets.store import get_default_ticket_store
from src.tickets.technicians import list_technicians as _list_technicians
from src.utils.logger import get_logger

logger = get_logger(__name__)

_DEPT_BY_CATEGORY = {
    "wifi": "IT Support",
    "hostel": "Hostel Administration",
    "facilities": "Facilities",
    "academics": "Registrar",
    "security": "Campus Security",
    "other": "General Help Desk",
}

_URGENT_PATTERN = re.compile(r"fire|harass|assault|safety|emergency", re.IGNORECASE)


def _score_urgency(category: str, description: str) -> str:
    if category == "security" or _URGENT_PATTERN.search(description):
        return "high"
    if category in ("hostel", "facilities"):
        return "medium"
    return "low"


@tool("Create Ticket")
def create_ticket(name: str, regno: str, category: str, description: str, hostel: str = "") -> str:
    """
    Logs a help-desk ticket for a student when their issue can't be
    resolved directly in conversation. `category` should be one of:
    wifi, hostel, facilities, academics, security, other. Returns the
    new ticket ID, assigned department, and urgency so you can tell the
    student what happens next. This does NOT assign a technician —
    that happens separately in the next Dispatch Agent pass.
    """
    department = _DEPT_BY_CATEGORY.get(category, "General Help Desk")
    urgency = _score_urgency(category, description)
    store = get_default_ticket_store()
    ticket = store.create(
        name=name,
        regno=regno,
        hostel=hostel,
        category=category,
        description=description,
        department=department,
        urgency=urgency,
    )
    return (
        f"Ticket {ticket.id} created — routed to {department}, urgency: {urgency}. "
        "A technician will be assigned during the next dispatch pass."
    )


@tool("List Open Tickets")
def list_open_tickets() -> str:
    """
    Lists every currently open (unassigned) help-desk ticket, with ID,
    department, urgency, hostel/location, and a short description. Use
    this first in a dispatch pass to see everything that needs assigning.
    """
    store = get_default_ticket_store()
    tickets = store.list_open()
    if not tickets:
        return "No open tickets."
    lines = [
        f"{t.id} | {t.department} | urgency={t.urgency} | hostel={t.hostel or 'n/a'} | {t.description[:80]}"
        for t in tickets
    ]
    return "\n".join(lines)


@tool("List Technicians")
def list_technicians() -> str:
    """
    Lists campus technicians with their department, skills, and
    availability. Use this to decide who each open ticket should go to.
    """
    techs = _list_technicians()
    if not techs:
        return "No technician roster configured."
    lines = [
        f"{t['name']} | {t['department']} | skills={', '.join(t.get('skills', []))} | "
        f"{'available' if t.get('available') else 'unavailable'}"
        for t in techs
    ]
    return "\n".join(lines)


@tool("Assign Ticket")
def assign_ticket(ticket_id: str, technician: str, scheduled_slot: str, note: str = "") -> str:
    """
    Assigns an open ticket to a technician for a time slot (e.g. 'today
    2-4pm', 'tomorrow morning'). Use `note` to record why this slot was
    chosen — urgency, weather, or grouping with a nearby ticket. Call
    this once per ticket you can place during a dispatch pass.
    """
    store = get_default_ticket_store()
    ticket = store.assign(ticket_id, technician, scheduled_slot, note)
    if not ticket:
        return f"No ticket found with ID {ticket_id}."
    return f"Ticket {ticket_id} assigned to {technician} for {scheduled_slot}."
