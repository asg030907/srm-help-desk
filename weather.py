"""
weather.py
Weather lookup tool. Plug in a real provider (OpenWeather, WeatherAPI,
etc.) in `_call_weather_provider`.
"""

import requests

from crewai.tools import tool

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _call_weather_provider(location: str) -> dict | None:
    """
    Calls the configured weather API. Example using OpenWeather's current
    weather endpoint:

        settings = get_settings()
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": settings.weather_api_key, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "location": data["name"],
            "temp_c": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
        }
    """
    settings = get_settings()
    if not settings.weather_api_key:
        logger.warning("WEATHER_API_KEY not set — cannot fetch live weather.")
        return None

    # Real provider call goes here once WEATHER_API_KEY is configured.
    return None


@tool("Weather Lookup")
def get_weather(location: str) -> str:
    """
    Fetches current weather conditions for a named location (city, or
    'city, country'). Use this whenever the user asks about weather,
    temperature, or whether they need an umbrella/jacket somewhere.
    """
    data = _call_weather_provider(location)
    if not data:
        return f"Weather data unavailable for '{location}' (weather provider not configured)."
    return f"{data['location']}: {data['temp_c']}°C, {data['condition']}."
