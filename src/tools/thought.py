"""Thought model."""


class Thought:
    """A Standardized response from any external tool to the agent."""

    def __init__(self, text=None, tool_calls=None, 
                raw_content=None, thinking=None):
        self.text = text
        self.tool_calls = tool_calls or []
        self.raw_content = raw_content # original API response for message history
        self.thinking = thinking
