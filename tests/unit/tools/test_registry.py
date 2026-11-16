from task_operator.tools import TOOL_FUNCTIONS, TOOLS, execute_tool


def test_every_schema_has_an_implementation():
    """Every tool the model is told about has a Python function behind it,
    and there are no functions without a description."""
    assert {t["name"] for t in TOOLS} == set(TOOL_FUNCTIONS)


def test_execute_tool_returns_result():
    """The dispatcher runs the named tool and returns its output."""
    assert execute_tool("calculate", {"expression": "2 + 2"}) == "4"


def test_execute_tool_turns_exceptions_into_error_strings():
    """A tool that crashes (divide by zero) gives back an "Error: ..." string
    instead of crashing the loop."""
    result = execute_tool("calculate", {"expression": "1 / 0"})
    assert result.startswith("Error: ZeroDivisionError")


def test_execute_tool_unknown_tool():
    """Asking for a tool that doesn't exist returns a clear error string."""
    assert execute_tool("launch_rockets", {}) == "Error: unknown tool 'launch_rockets'."


def test_execute_tool_bad_arguments():
    """Calling a tool with the wrong argument name returns an error string."""
    assert execute_tool("get_weather", {"town": "Tokyo"}).startswith("Error: TypeError")
