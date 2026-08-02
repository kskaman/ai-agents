"""Fake brain for testing."""

from .brain import Brain
from ..tools import Thought


class FakeBrain(Brain):
    """A fake brain (generates LLM-like responses) that can be used for testing purposes."""

    def __init__(self, responses=None, tools=None):
        self.tools = tools or []

        self.responses = responses or [
            Thought(
                text="Fake response",
                raw_content=[{"type": "text", "text":"Fake response"}]
            )
        ]

        self.call_count = 0
        self.last_conversation = None

    def think(self, conversation):
        """Simulate thinking by returning a pre-defined response."""
        self.last_conversation = list(conversation)  # Store a copy of the conversation

        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        return Thought(
            text="No more responses.",
            raw_content=[{
                "type": "text", "text":"No more responses."
            }]
        )