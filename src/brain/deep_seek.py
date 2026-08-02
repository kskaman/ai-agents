"""DeepSeek brain implementation."""

import os
from .brain import Brain
from ..utils import request_with_retry


class DeepSeek(Brain):
    """DeepSeek API (Anthropic Compatible)."""
    def __init__(self, memory = None, tools = None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.memory = memory
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found.")
        self.tools = tools or []
        self.model = "deepseek-chat"
        self.url = "https://api.deepseek.com/anthropic/v1/messages"


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
            "system": "You are a helpful coding assistant. Always respond in English.",
            "messages": conversation
        }

        if self.memory:
            payload["system"] = self.memory.content
        if self.tools:
            payload["tools"] = self.tools
            
        response = request_with_retry(self.url, headers, payload)
        response.raise_for_status()
        return self._parse_response(response.json()["content"])

