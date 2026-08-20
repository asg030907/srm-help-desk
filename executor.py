"""
executor.py
Runs a single conversational turn of the Intake Agent (agent #1 of 2):
pulls conversation state from memory, builds a task for the agent,
executes it via a one-agent Crew, and persists the updated state. This
is the module the /api/chat route calls — one run per chat message.

Agent #2, the Dispatch Agent, lives in dispatch_executor.py and is
never called from here — it runs on its own schedule.
"""

from crewai import Crew, Process, Task

from src.agent.agent import build_intake_agent
from src.agent.memory import MemoryStore, get_default_store
from src.prompts.agent_prompts import task_prompt
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentExecutor:
    """Wraps Intake Agent construction + crew execution behind a simple run() call."""

    def __init__(self, memory_store: MemoryStore | None = None) -> None:
        self.memory_store = memory_store or get_default_store()
        self.agent = build_intake_agent()

    def run(self, message: str, session_id: str | None = None) -> dict:
        """
        Run one turn of conversation.
        Returns {"session_id": ..., "response": ...}.
        """
        state = self.memory_store.get_or_create(session_id)
        state.add_message("user", message)

        context = state.history_as_text(max_turns=8)
        description = task_prompt(user_message=message, context=context)

        task = Task(
            description=description,
            expected_output="A direct, helpful answer to the user's message.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=True)

        logger.info("Running turn for session=%s", state.session_id)
        result = crew.kickoff()
        response_text = str(result)

        state.add_message("assistant", response_text)
        self.memory_store.save(state)

        return {"session_id": state.session_id, "response": response_text}
