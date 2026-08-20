"""
config.py
Centralized application settings, loaded from environment variables / .env.
Every other module reads configuration through `get_settings()` rather than
calling os.getenv() directly, so there's exactly one place that knows about
env var names and defaults.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    anthropic_api_key: str = ""
    agent_llm_model: str = "anthropic/claude-sonnet-4-5-20250929"

    # Tool provider keys
    search_api_key: str = ""
    weather_api_key: str = ""

    # App
    log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins_raw: str = Field(default="*", alias="ALLOWED_ORIGINS")

    # Tickets / Dispatch Agent
    tickets_db_path: str = "data/tickets.db"
    technicians_path: str = "data/technicians.json"
    campus_location: str = "Kattankulathur, Chengalpattu, Tamil Nadu"
    dispatch_interval_minutes: int = 15

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated ALLOWED_ORIGINS env var into a list."""
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — call this instead of instantiating Settings() directly."""
    return Settings()
