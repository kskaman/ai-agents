"""Tool: current weather (a stub with canned data - no network call)."""

_WEATHER = {
    "san francisco": "62°F, foggy",
    "tokyo": "71°F, clear",
    "london": "55°F, light rain",
    "new york": "68°F, partly cloudy",
}


def get_weather(city: str) -> str:
    """Return canned weather data for a known city."""
    weather = _WEATHER.get(city.strip().lower())
    if weather is None:
        known = ", ".join(c.title() for c in _WEATHER)
        raise ValueError(f"No weather data for {city!r}. Known cities: {known}.")
    return f"{city.strip().title()}: {weather}"


SCHEMA = {
    "name": "get_weather",
    "description": "Get the current weather (temperature in °F and conditions) for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Tokyo'."}
        },
        "required": ["city"],
    },
}
