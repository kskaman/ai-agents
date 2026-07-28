"""Thought model."""


class Thought:
    """A Standardized response from any external tool to the agent."""

    def __init__(self, text=None, tool_calls=None, thinking=None):
        self.text = text
        self.tool_calls = tool_calls or []
        self.thinking = thinking
