import os
import requests

from .brain import Brain
from ..utils import request_with_retry

class Ollama(Brain):
    """Ollama local modal (Anthropic Compatible API, with tool support)."""
    context_limit = 128_000  # 128k tokens

    def __init__(self, memory=None, tools=None):
        self.memory = memory
        self.system = None
        self.tools = tools or []
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.url = "http://localhost:11434/v1/messages"
        self.last_input_tokens = 0

        self._detect_context_limit()

    def _detect_context_limit(self):
        """Query Ollama for the model's context window size."""
        try:
            response = requests.post(
                "http://localhost:11434/api/show",
                json={"model": self.model},
                timeout=2
            )

            model_info = response.json().get("model_info", {})
            for key, value in model_info.items():
                if key.endswith(".context_length"):
                    self.context_limit = value
                    return
        except Exception:
            pass # Keep default context limit if detection fails

    def think(self, conversation, thinking_budget=3000):
        headers = {
            "x-api-key": "ollama",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": conversation
        }

        if self.system:
            payload["system"] = self.system
        if self.tools:
            payload["tools"] = self.tools

        response = request_with_retry(self.url, headers=headers, payload=payload)
        response.raise_for_status()
        data = response.json()
        self.last_input_tokens = data.get("usage", {}).get("input_tokens", 0)
        return self._parse_response(data["content"])        
