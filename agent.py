"""
agent.py
Constructs the CrewAI agent(s) used by this project, wiring together the
LLM client, tools, and prompt templates. Executor.py / dispatch_executor.py
are responsible for actually running a turn — this module only builds
the agent objects.

Two agents live here, each with its own tools and its own trigger:
  - Intake Agent  — runs once per chat message (AgentExecutor).
  - Dispatch Agent — runs on a timer, never per-message (DispatchExecutor).
They never call each other directly; they hand work off through the
shared ticket store in src/tickets/.
"""

from crewai import Agent

from src.models.llm_client import get_llm
from src.prompts.agent_prompts import dispatch_agent_prompts, general_assistant_prompts, intake_agent_prompts
from src.tools.calculator import calculate
from src.tools.search import web_search
from src.tools.ticketing import assign_ticket, create_ticket, list_open_tickets, list_technicians
from src.tools.weather import get_weather
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_general_assistant() -> Agent:
    """Construct the plain general-purpose assistant agent (no ticketing tools)."""
    prompts = general_assistant_prompts()
    logger.info("Building general assistant agent")
    return Agent(
        role=prompts["role"],
        goal=prompts["goal"],
        backstory=prompts["backstory"],
        tools=[web_search, calculate, get_weather],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_intake_agent() -> Agent:
    """
    Agent #1 — the one students actually talk to (via /api/chat). Tries
    to resolve things inline; logs a ticket via the Create Ticket tool
    when a real technician is needed. Never assigns technicians itself.
    """
    prompts = intake_agent_prompts()
    logger.info("Building intake agent")
    return Agent(
        role=prompts["role"],
        goal=prompts["goal"],
        backstory=prompts["backstory"],
        tools=[web_search, calculate, get_weather, create_ticket],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_dispatch_agent() -> Agent:
    """
    Agent #2 — runs on a timer (see main.py / dispatch_executor.py),
    never in response to a chat message. Reads the open ticket queue
    and technician roster and assigns work in one batch pass.
    """
    prompts = dispatch_agent_prompts()
    logger.info("Building dispatch agent")
    return Agent(
        role=prompts["role"],
        goal=prompts["goal"],
        backstory=prompts["backstory"],
        tools=[list_open_tickets, list_technicians, assign_ticket, get_weather, calculate],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
