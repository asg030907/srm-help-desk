"""
search.py
Web search tool. Plug in a real search provider (Serper, Tavily, Bing,
etc.) in `_call_search_provider` — the tool contract stays the same.
"""

import requests

from crewai.tools import tool

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _call_search_provider(query: str, num_results: int = 5) -> list[dict]:
    """
    Calls the configured search API. Swap this implementation for your
    provider of choice. Example using a generic Serper-style API:

        settings = get_settings()
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.search_api_key},
            json={"q": query, "num": num_results},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {"title": r["title"], "link": r["link"], "snippet": r.get("snippet", "")}
            for r in data.get("organic", [])[:num_results]
        ]
    """
    settings = get_settings()
    if not settings.search_api_key:
        logger.warning("SEARCH_API_KEY not set — returning empty search results.")
        return []

    # Real provider call goes here once SEARCH_API_KEY is configured.
    return []


@tool("Web Search")
def web_search(query: str) -> str:
    """
    Searches the web for a query and returns a short list of results
    (title, link, snippet). Use this when the user asks about current
    events, facts you're unsure of, or anything time-sensitive.
    """
    results = _call_search_provider(query)
    if not results:
        return f"No search results available for '{query}' (search provider not configured)."

    lines = [f"{i+1}. {r['title']} — {r['snippet']} ({r['link']})" for i, r in enumerate(results)]
    return "\n".join(lines)
