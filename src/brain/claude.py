"""Claude brain implementation."""

import os
from .brain import Brain
from ..utils import request_with_retry


class Claude(Brain):
    """Claude API - the brain of our agent."""
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


    def think(self, conversation, thinking_budget=None):
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
                "budget_tokens": thinking_budget or 3000
            },
            "system": self.system or "You are a helpful coding assistant. Always respond in English.",
            "messages": conversation
        }

        if self.tools:
            payload["tools"] = self.tools
            
        response = request_with_retry(self.url, headers, payload)
        response.raise_for_status()
        data = response.json()
        self.last_input_tokens = data.get("usage", {}).get("input_tokens", 0)
        return self._parse_response(data["content"])

