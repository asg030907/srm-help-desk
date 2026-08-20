"""
test_tickets.py
Unit tests for the ticket store shared by the Intake and Dispatch agents.
"""

import tempfile
from pathlib import Path

from src.tickets.store import TicketStore


def _tmp_store() -> TicketStore:
    tmp = Path(tempfile.mkdtemp()) / "tickets.db"
    return TicketStore(str(tmp))


def test_create_and_list_open():
    store = _tmp_store()
    store.create(
        name="Asha", regno="RA2211", hostel="N Block", category="wifi",
        description="WiFi down since morning", department="IT Support", urgency="medium",
    )
    open_tickets = store.list_open()
    assert len(open_tickets) == 1
    assert open_tickets[0].department == "IT Support"
    assert open_tickets[0].status == "open"


def test_assign_moves_ticket_out_of_open():
    store = _tmp_store()
    ticket = store.create(
        name="Ravi", regno="RA2299", hostel="", category="security",
        description="Broken gate lock", department="Campus Security", urgency="high",
    )
    store.assign(ticket.id, technician="Security Desk", scheduled_slot="today", note="urgent")

    assert store.list_open() == []
    updated = store.get(ticket.id)
    assert updated.status == "assigned"
    assert updated.assigned_technician == "Security Desk"


def test_open_tickets_ordered_by_urgency():
    store = _tmp_store()
    store.create(name="A", regno="1", hostel="", category="wifi", description="slow",
                 department="IT Support", urgency="low")
    store.create(name="B", regno="2", hostel="", category="security", description="fire alarm",
                 department="Campus Security", urgency="high")

    open_tickets = store.list_open()
    assert open_tickets[0].urgency == "high"
