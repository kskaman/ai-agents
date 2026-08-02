"""Models for the coding agent."""

from .thought import Thought
from .tool_call import ToolCall
from .read_file import ReadFile
from .write_file import WriteFile
from .tool_helpers import get_tool, tool_definitions

tools = [ReadFile(), WriteFile()]

__all__ = ["Thought", "ToolCall", "tools", "get_tool", "tool_definitions"]
