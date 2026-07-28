"""Claude brain implementation."""

import os
from .brain import Brain
from src.utils import request_with_retry


class Claude(Brain):
    """Claude API - the brain of our agent."""
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found.")

        self.model = "claude-sonnet-4-6"
        self.url = "https://api.anthropic.com/v1/messages"


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
            "messages": conversation
        }

        response = request_with_retry(self.url, headers, payload)
        response.raise_for_status()
        return self._parse_response(response.json()["content"])

