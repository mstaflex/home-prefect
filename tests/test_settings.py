"""Tests for the Settings model."""

import pytest

from home_prefect.config.settings import Settings


def test_settings_defaults() -> None:
    s = Settings()
    assert s.prefect_api_url == "http://localhost:4200/api"
    assert s.log_level == "INFO"


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PREFECT_API_URL", "http://server:4200/api")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = Settings()
    assert s.prefect_api_url == "http://server:4200/api"
    assert s.log_level == "DEBUG"
