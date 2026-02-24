"""Central application settings loaded from environment variables / .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All tuneable parameters, sourced from environment or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Prefect ──────────────────────────────────────────────────────────────
    prefect_api_url: str = Field(
        default="http://localhost:4200/api",
        description="URL of the Prefect API this process connects to.",
    )

    # ── Application ──────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO", description="Root log level.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""
    return Settings()
