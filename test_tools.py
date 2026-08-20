"""
test_tools.py
Tests for the individual tools. Search and weather are tested against
their "provider not configured" fallback path so no API keys are
required to run the suite.

`_invoke` handles the fact that CrewAI's @tool decorator interface has
changed across versions (some expose `.func(...)`, others require
`.run(...)`) -- it tries both so these tests don't break on a minor
version bump.
"""

from src.tools.calculator import calculate
from src.tools.search import web_search
from src.tools.weather import get_weather


def _invoke(tool_obj, **kwargs):
    if hasattr(tool_obj, "func"):
        return tool_obj.func(**kwargs)
    return tool_obj.run(**kwargs)


def test_calculate_basic_arithmetic():
    assert _invoke(calculate, expression="2 + 2") == "4"
    assert _invoke(calculate, expression="10 / 4") == "2.5"
    assert _invoke(calculate, expression="2 ** 5") == "32"


def test_calculate_rejects_unsafe_expression():
    result = _invoke(calculate, expression="__import__('os').system('echo hi')")
    assert "Could not evaluate" in result


def test_web_search_without_api_key_returns_message():
    result = _invoke(web_search, query="SRM Institute of Science and Technology")
    assert isinstance(result, str) and len(result) > 0


def test_get_weather_without_api_key_returns_message():
    result = _invoke(get_weather, location="Chennai")
    assert isinstance(result, str) and len(result) > 0
