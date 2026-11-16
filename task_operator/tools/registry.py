"""The tool registry: which tools the agent may use, and how a call is run.

To add a tool: create a module with a function and a SCHEMA, then add one
(SCHEMA, function) pair to _REGISTERED below.
"""

from task_operator.tools import calculator, text, weather

_REGISTERED = [
    (calculator.SCHEMA, calculator.calculate),
    (weather.SCHEMA, weather.get_weather),
    (text.SCHEMA, text.count_characters),
]

# What the model is told about (sent with every request).
TOOLS = [schema for schema, _ in _REGISTERED]

# What actually runs when the model asks for a tool by name.
TOOL_FUNCTIONS = {schema["name"]: func for schema, func in _REGISTERED}


def execute_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call. Never raises: errors come back as strings so the
    model can observe them and decide what to do next."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Error: unknown tool {name!r}."
    try:
        return func(**tool_input)
    except Exception as e:  # noqa: BLE001 - every failure becomes an observation
        return f"Error: {type(e).__name__}: {e}"
