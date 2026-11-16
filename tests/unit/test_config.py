"""Tests for task_operator.config. They pass a plain dict as the environment,
so they never read the real .env file or your API key."""

import pytest

from task_operator.config import ConfigError, env_or_throw, load_config, validate_type

# --- env_or_throw --------------------------------------------------------------


def test_env_or_throw_returns_value():
    """A variable that is set comes back as-is (surrounding spaces trimmed)."""
    assert env_or_throw("KEY", {"KEY": " abc "}) == "abc"


@pytest.mark.parametrize("environ", [{}, {"KEY": ""}, {"KEY": "   "}])
def test_env_or_throw_raises_when_missing_or_blank(environ):
    """A missing, empty or blank variable raises an error naming the variable."""
    with pytest.raises(ConfigError, match="KEY"):
        env_or_throw("KEY", environ)


# --- validate_type -------------------------------------------------------------


def test_validate_type_str_is_unchanged():
    """Strings are returned untouched."""
    assert validate_type("X", "hello", str) == "hello"


def test_validate_type_int():
    """A numeric string becomes an int."""
    assert validate_type("X", "42", int) == 42


def test_validate_type_int_rejects_text():
    """Non-numeric text for an int variable raises a clear error."""
    with pytest.raises(ConfigError, match="must be an integer"):
        validate_type("X", "ten", int)


@pytest.mark.parametrize("raw, expected", [("true", True), ("YES", True), ("1", True),
                                           ("false", False), ("off", False), ("0", False)])
def test_validate_type_bool(raw, expected):
    """Common true/false spellings are accepted, in any case."""
    assert validate_type("X", raw, bool) is expected


def test_validate_type_bool_rejects_other_text():
    """Anything that isn't a recognised true/false word raises."""
    with pytest.raises(ConfigError, match="true/false"):
        validate_type("X", "maybe", bool)


def test_validate_type_unsupported_type():
    """Asking for a type the validator doesn't know is a programming error."""
    with pytest.raises(TypeError):
        validate_type("X", "1.5", float)


# --- load_config ---------------------------------------------------------------


def test_load_config_applies_defaults():
    """With only the required key set, optional variables get their defaults."""
    config = load_config({"ANTHROPIC_API_KEY": "sk-test"})
    assert config == {
        "ANTHROPIC_API_KEY": "sk-test",
        "TASK_OPERATOR_MAX_ITERATIONS": 10,
        "TASK_OPERATOR_VERBOSE": True,
    }


def test_load_config_converts_types():
    """Values from the environment are converted to their declared types."""
    config = load_config({
        "ANTHROPIC_API_KEY": "sk-test",
        "TASK_OPERATOR_MAX_ITERATIONS": "3",
        "TASK_OPERATOR_VERBOSE": "false",
    })
    assert config["TASK_OPERATOR_MAX_ITERATIONS"] == 3
    assert config["TASK_OPERATOR_VERBOSE"] is False


def test_load_config_reports_all_errors_at_once():
    """Every problem is listed in one error, so you can fix .env in one go."""
    with pytest.raises(ConfigError) as exc:
        load_config({"TASK_OPERATOR_MAX_ITERATIONS": "lots"})
    message = str(exc.value)
    assert "ANTHROPIC_API_KEY" in message
    assert "TASK_OPERATOR_MAX_ITERATIONS" in message
