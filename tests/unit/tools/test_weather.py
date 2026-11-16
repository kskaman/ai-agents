import pytest

from task_operator.tools.weather import get_weather


def test_get_weather_known_city_is_case_insensitive():
    """City lookup ignores capitalisation and extra spaces."""
    assert get_weather("  tokyo ") == "Tokyo: 71°F, clear"


def test_get_weather_unknown_city_lists_known_cities():
    """An unknown city raises an error that tells the model which cities exist,
    so it can retry with a valid one."""
    with pytest.raises(ValueError, match="Known cities"):
        get_weather("Atlantis")
