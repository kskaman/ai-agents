"""All environment variables the app uses, loaded and validated once at startup.

Add a new variable by adding one entry to ENV_VARS. Everything else reads
values from get_config(), never from os.environ directly.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from functools import cache

from dotenv import load_dotenv

# name -> expected type, and either required=True or a default value.
ENV_VARS: dict[str, dict] = {
    "ANTHROPIC_API_KEY": {"type": str, "required": True},
    "TASK_OPERATOR_MAX_ITERATIONS": {"type": int, "default": 10},
    "TASK_OPERATOR_VERBOSE": {"type": bool, "default": True},
}

_TRUE = {"true", "1", "yes", "on"}
_FALSE = {"false", "0", "no", "off"}


class ConfigError(RuntimeError):
    """Raised when an environment variable is missing or has the wrong type."""


def env_or_throw(name: str, environ: Mapping[str, str] = os.environ) -> str:
    """Return the raw value of `name`, or raise if it is missing or empty."""
    value = environ.get(name)
    if value is None or not value.strip():
        raise ConfigError(
            f"Missing required environment variable {name}. "
            "Add it to .env (see .env.example)."
        )
    return value.strip()


def validate_type(name: str, raw: str, expected: type):
    """Convert the raw string from the environment to `expected`, or raise."""
    if expected is str:
        return raw
    if expected is int:
        try:
            return int(raw)
        except ValueError:
            raise ConfigError(f"{name} must be an integer, got {raw!r}.") from None
    if expected is bool:
        lowered = raw.lower()
        if lowered in _TRUE:
            return True
        if lowered in _FALSE:
            return False
        raise ConfigError(f"{name} must be true/false (or 1/0, yes/no, on/off), got {raw!r}.")
    raise TypeError(f"Unsupported config type {expected.__name__} for {name}.")


def load_config(environ: Mapping[str, str] = os.environ) -> dict:
    """Read and validate every variable in ENV_VARS.

    Collects all problems and raises them together, so you fix .env in one go.
    """
    config: dict = {}
    errors: list[str] = []
    for name, spec in ENV_VARS.items():
        try:
            if spec.get("required"):
                raw = env_or_throw(name, environ)
            else:
                raw = environ.get(name, "").strip()
                if not raw:
                    config[name] = spec["default"]
                    continue
            config[name] = validate_type(name, raw, spec["type"])
        except ConfigError as e:
            errors.append(str(e))
    if errors:
        raise ConfigError("Invalid configuration:\n  - " + "\n  - ".join(errors))
    return config


@cache
def get_config() -> dict:
    """Load .env and validate it on the first call; later calls reuse the result."""
    load_dotenv()
    return load_config()
