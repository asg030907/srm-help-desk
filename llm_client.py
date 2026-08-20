"""
llm_client.py
Single place that constructs the LLM instance used by the agent, so the
model/provider can be swapped by editing .env only.
"""

from functools import lru_cache

from crewai import LLM

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_llm(temperature: float = 0.2) -> LLM:
    """
    Return a configured CrewAI LLM instance.
    Cached per temperature value so repeated calls reuse the same client.
    """
    settings = get_settings()
    logger.info("Initializing LLM client: model=%s temperature=%s", settings.agent_llm_model, temperature)
    return LLM(
        model=settings.agent_llm_model,
        temperature=temperature,
    )
