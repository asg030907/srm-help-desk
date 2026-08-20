"""
state.py
Data model for a single conversation's state. Kept separate from memory.py:
`state.py` defines *what* a conversation looks like, `memory.py` defines
*how it's stored and retrieved* across turns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Role = Literal["user", "assistant", "system"]


@dataclass
class Message:
    role: Role
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationState:
    session_id: str
    messages: list[Message] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add_message(self, role: Role, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def history_as_text(self, max_turns: int = 10) -> str:
        """Render the last `max_turns` messages as plain text for prompt context."""
        recent = self.messages[-max_turns:]
        return "\n".join(f"{m.role.upper()}: {m.content}" for m in recent)

    def last_user_message(self) -> str | None:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return None
