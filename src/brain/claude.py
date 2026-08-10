"""Claude brain implementation."""

import os
from .brain import Brain


class Claude(Brain):
    """Claude API - the brain of our agent."""
    streams_output = True

    def __init__(self, memory=None, tools = None):
        self.memory = memory
        self.system = None
        self.tools = tools or []
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found.")

        self.model = "claude-sonnet-4-6"
        self.url = "https://api.anthropic.com/v1/messages"

        self.last_input_tokens = 0


    def think(self, conversation):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": 16000,
            "thinking": {
                "type": "enabled",
                "budget_tokens": 10000
            },
            "system": self.system or "You are a helpful coding assistant. Always respond in English.",
            "messages": conversation,
            "stream": True,
        }

        if self.tools:
            payload["tools"] = self.tools

        return self._stream_response(self.url, headers, payload)
