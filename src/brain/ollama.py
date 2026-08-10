import os
import requests

from .brain import Brain

class Ollama(Brain):
    """Ollama local modal (Anthropic Compatible API, with tool support)."""
    context_limit = 128_000  # 128k tokens
    streams_output = True

    def __init__(self, memory=None, tools=None):
        self.memory = memory
        self.system = None
        self.tools = tools or []
        self.model = os.getenv("OLLAMA_MODEL", "qwen3-coder:30b")
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

    def think(self, conversation):
        headers = {
            "x-api-key": "ollama",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": conversation,
            "stream": True,
        }

        if self.system:
            payload["system"] = self.system
        if self.tools:
            payload["tools"] = self.tools
        
        return self._stream_response(self.url, headers, payload)
