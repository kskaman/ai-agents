"""Shared test setup: every unit test runs against a fake, known config."""

import pytest

from task_operator.config import ENV_VARS, get_config


@pytest.fixture(autouse=True)
def fake_config(monkeypatch):
    """Code now reads settings via get_config(). For tests, make that return
    a fake key and the defaults, and never read the real .env file."""
    monkeypatch.setattr("task_operator.config.config.load_dotenv", lambda: None)
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    get_config.cache_clear()
    yield
    get_config.cache_clear()
