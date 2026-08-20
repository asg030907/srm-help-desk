"""
schemas.py
Request/response models for the API layer.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message to the agent.")
    session_id: str | None = Field(
        default=None, description="Existing session ID to continue a conversation, or omit to start a new one."
    )


class ChatResponse(BaseModel):
    session_id: str
    response: str


class HealthResponse(BaseModel):
    status: str = "ok"


class TicketOut(BaseModel):
    id: str
    name: str
    regno: str
    hostel: str
    category: str
    description: str
    department: str
    urgency: str
    status: str
    assigned_technician: str | None = None
    scheduled_slot: str | None = None
    dispatch_note: str | None = None
    created_at: str
    updated_at: str


class DispatchRunResponse(BaseModel):
    summary: str
