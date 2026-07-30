"""Tool call model."""


class ToolCall:
    """A tool invocation request from the agent to an external tool."""

    def __init__(self, id, tool_name, args):
        self.id = id
        self.tool_name = tool_name
        self.args = args
