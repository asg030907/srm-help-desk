"""
memory.py
Conversation memory store. Ships with a simple in-process dict-backed
store so the project runs with zero external dependencies; swap
`InMemoryStore` for a Redis/Postgres-backed implementation for
multi-process deployments — callers only depend on the `MemoryStore`
interface below.
"""

from abc import ABC, abstractmethod

from src.agent.state import ConversationState
from src.utils.helpers import new_id
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryStore(ABC):
    @abstractmethod
    def get_or_create(self, session_id: str | None) -> ConversationState: ...

    @abstractmethod
    def save(self, state: ConversationState) -> None: ...

    @abstractmethod
    def clear(self, session_id: str) -> None: ...


class InMemoryStore(MemoryStore):
    """Process-local memory store. Not shared across workers/restarts."""

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get_or_create(self, session_id: str | None) -> ConversationState:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        new_session_id = session_id or new_id("session")
        state = ConversationState(session_id=new_session_id)
        self._sessions[new_session_id] = state
        logger.info("Created new conversation state: %s", new_session_id)
        return state

    def save(self, state: ConversationState) -> None:
        self._sessions[state.session_id] = state

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


_default_store = InMemoryStore()


def get_default_store() -> MemoryStore:
    """Process-wide default memory store used by the executor unless overridden."""
    return _default_store
