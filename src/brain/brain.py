"""Base brain class."""

from ..tools import Thought, ToolCall


class Brain:
    """Base class for LLM providers."""

    def think(self, conversation: list[dict]) -> Thought:
        """Process conversation, return Thought."""
        raise NotImplementedError()

    def _parse_response(self, content: list[dict]) -> Thought:
            """Convert Claude's response into a Thought object."""
            text_parts = []
            tool_calls = []
            thinking = None
    
            for block in content:
                if block["type"] == "thinking":
                    thinking = block["thinking"]
                elif block["type"] == "text":
                    text_parts.append(block["text"])
                elif block["type"] == "tool_call":
                    tool_calls.append(ToolCall(
                        id=block["id"],
                        tool_name=block["tool_name"],
                        args=block["input"]
                    ))
    
            return Thought(
                text="\n".join(text_parts) if text_parts else None,
                tool_calls=tool_calls,
                thinking=thinking
            )
