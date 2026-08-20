"""
test_agent.py
Tests for agent construction and conversation state/memory — these run
without any LLM API key since they don't call kickoff().
"""

from src.agent.memory import InMemoryStore
from src.agent.state import ConversationState


def test_conversation_state_tracks_messages():
    state = ConversationState(session_id="test-session")
    state.add_message("user", "hello")
    state.add_message("assistant", "hi there")

    assert len(state.messages) == 2
    assert state.last_user_message() == "hello"


def test_history_as_text_formats_recent_messages():
    state = ConversationState(session_id="test-session")
    state.add_message("user", "what's 2+2?")
    state.add_message("assistant", "4")

    text = state.history_as_text()
    assert "USER: what's 2+2?" in text
    assert "ASSISTANT: 4" in text


def test_in_memory_store_creates_and_reuses_sessions():
    store = InMemoryStore()

    state = store.get_or_create(None)
    assert state.session_id.startswith("session-")

    same_state = store.get_or_create(state.session_id)
    assert same_state is state


def test_in_memory_store_clear_removes_session():
    store = InMemoryStore()
    state = store.get_or_create("to-clear")
    store.clear("to-clear")

    new_state = store.get_or_create("to-clear")
    assert new_state is not state
    assert new_state.messages == []
