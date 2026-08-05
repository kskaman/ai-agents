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
            filtered_content = []
    
            for block in content:
                if block["type"] == "thinking":
                    thinking = block["thinking"]
                    # Don't include thinking blocks in conversation history
                elif block["type"] == "text":
                    text_parts.append(block["text"])
                    filtered_content.append(block)
                elif block["type"] == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block["id"],
                        tool_name=block["name"],
                        args=block["input"]
                    ))
                    filtered_content.append(block)
    
            return Thought(
                text="\n".join(text_parts) if text_parts else None,
                tool_calls=tool_calls,
                raw_content=filtered_content,  # Only text and tool_use blocks
                thinking=thinking
            )