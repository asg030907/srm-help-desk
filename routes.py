"""
routes.py
FastAPI routes for interacting with the two agents. Mounted under /api
by main.py.

- POST /api/chat        -> Intake Agent (one run per request)
- GET  /api/tickets      -> read the shared ticket queue either agent touched
- POST /api/dispatch/run -> Dispatch Agent, run on demand instead of
                             waiting for the scheduled interval
"""

from fastapi import APIRouter, HTTPException

from src.agent.dispatch_executor import DispatchExecutor
from src.agent.executor import AgentExecutor
from src.api.schemas import ChatRequest, ChatResponse, DispatchRunResponse, HealthResponse, TicketOut
from src.tickets.store import get_default_ticket_store
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# One executor per process; the underlying agent/LLM client is stateless
# and safe to reuse across requests. Conversation state lives in the
# memory store, keyed by session_id.
_executor = AgentExecutor()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Runs the Intake Agent for one turn — this is the agent students talk to."""
    try:
        result = _executor.run(message=request.message, session_id=request.session_id)
        return ChatResponse(**result)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Intake agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets() -> list[TicketOut]:
    """Returns every ticket (open or assigned) — the shared state both agents read/write."""
    store = get_default_ticket_store()
    return [TicketOut(**vars(t)) for t in store.list_all()]


@router.post("/dispatch/run", response_model=DispatchRunResponse)
def run_dispatch() -> DispatchRunResponse:
    """
    Manually triggers a Dispatch Agent pass — the same thing the
    background scheduler runs automatically every
    DISPATCH_INTERVAL_MINUTES. Useful for demos/testing without
    waiting for the timer.
    """
    try:
        result = DispatchExecutor().run()
        return DispatchRunResponse(**result)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Dispatch agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
