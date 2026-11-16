"""Tool: basic arithmetic."""

_ALLOWED = set("0123456789+-*/().% ")


def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    if not expression or not set(expression) <= _ALLOWED:
        raise ValueError(
            f"Invalid characters in expression {expression!r}. "
            "Only digits, + - * / % ( ) . and spaces are allowed."
        )
    if "**" in expression:
        # 9**9**9 would hang the process; the shell decides what is safe to run.
        raise ValueError("Exponentiation (**) is not supported.")
    result = eval(expression, {"__builtins__": {}}, {})  # safe: input allowlisted above
    return str(result)


SCHEMA = {
    "name": "calculate",
    "description": (
        "Evaluate an arithmetic expression and return the numeric result. "
        "Supports + - * / % and parentheses. Use this for any math instead "
        "of computing in your head."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The expression to evaluate, e.g. '(71 - 32) * 5 / 9'.",
            }
        },
        "required": ["expression"],
    },
}
