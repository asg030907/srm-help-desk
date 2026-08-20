"""
dispatch_executor.py
Runs one batch Dispatch Agent pass (agent #2 of 2): builds the Dispatch
Agent, gives it a single task covering the whole open-ticket queue, and
lets it call the ticketing tools to assign work.

Unlike AgentExecutor (agent #1), this is never triggered by a chat
message. It's called on a timer from main.py's scheduler, or manually
via POST /api/dispatch/run.
"""

from crewai import Crew, Process, Task

from src.agent.agent import build_dispatch_agent
from src.prompts.agent_prompts import dispatch_task_prompt
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DispatchExecutor:
    """Wraps Dispatch Agent construction + one batch run() call."""

    def __init__(self) -> None:
        self.agent = build_dispatch_agent()

    def run(self) -> dict:
        """
        Run one dispatch pass over all open tickets.
        Returns {"summary": ...} — the agent's own account of what it assigned.
        """
        settings = get_settings()
        description = dispatch_task_prompt(campus_location=settings.campus_location)

        task = Task(
            description=description,
            expected_output="A short summary of tickets assigned and any left open, with reasons.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=True)

        logger.info("Running dispatch pass")
        result = crew.kickoff()
        summary = str(result)
        logger.info("Dispatch pass complete: %s", summary)
        return {"summary": summary}
