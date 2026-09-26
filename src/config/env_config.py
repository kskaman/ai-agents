import math
import os

from dotenv import load_dotenv

load_dotenv()


class EnvironmentConfigError(RuntimeError):
    """Raised when an environment variable is missing or invalid."""


def get_env_variable(
    name: str,
    default: str | None = None,
    *,
    required: bool = False,
) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        if required:
            raise EnvironmentConfigError(
                f"Environment variable '{name}' is required and must not be empty."
            )
        return "" if value is None else value
    return value.strip()


def get_env_float(name: str, default: float) -> float:
    raw_value = get_env_variable(name, str(default))
    try:
        value = float(raw_value)
    except ValueError as error:
        raise EnvironmentConfigError(
            f"Environment variable '{name}' must be a number."
        ) from error

    if not math.isfinite(value) or value < 0:
        raise EnvironmentConfigError(
            f"Environment variable '{name}' must be a non-negative finite number."
        )
    return value


def get_provider_name(override: str | None = None) -> str:
    provider = (override or get_env_variable("PROVIDER", "anthropic")).lower()
    if provider not in {"anthropic", "openai"}:
        raise EnvironmentConfigError(
            "Environment variable 'PROVIDER' must be 'anthropic' or 'openai'."
        )
    return provider


def get_provider_model(provider: str, override: str | None = None) -> str:
    if override:
        return override
    variable_name = "ANTHROPIC_MODEL" if provider == "anthropic" else "OPENAI_MODEL"
    return get_env_variable(variable_name, required=True)


def validate_provider_api_key(provider: str) -> None:
    variable_name = (
        "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    )
    api_key = get_env_variable(variable_name, required=True)
    