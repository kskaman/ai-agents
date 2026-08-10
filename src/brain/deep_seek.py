"""DeepSeek brain implementation."""

import os
from .brain import Brain


class DeepSeek(Brain):
    context_limit = 128_000  # 128k tokens
    streams_output = True
    
    """DeepSeek API (Anthropic Compatible)."""
    def __init__(self, memory = None, tools = None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.memory = memory
        self.system = None
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
            "max_tokens": 4096,
            "system": self.system or "You are a helpful coding assistant. Always respond in English.",
            "messages": conversation,
            "stream": True,
        }
        if self.tools:
            payload["tools"] = self.tools

        return self._stream_response(self.url, headers, payload)
