from config.env_config import (
    get_provider_model,
    get_provider_name,
    validate_provider_api_key,
)
from .llm import CostTracker, LLMClient, LLMConfig, Provider
from rich.console import Console
from rich.panel import Panel

DEBUG_STYLES = {
    "THINKING": "cyan",
    "ACTION": "yellow",
    "RESULT": "green",
}

SYSTEM_PROMPT = """You are RTE, an AI agent for research and task
execution.

## Behavior
- Be direct and to the point. Avoid beating around the bush.
- When you don't know something, say so clearly instead of making things up.
- Prefer structured responses with lists and sections when appropriate.
- Cite sources whenever possible.

## Limitations
- You don't have access to external tools yet (that's coming soon).
- Your knowledge has a cutoff date. Let the user know when a question
 requires more recent information.

## Tone
- Professional but approachable.
- Like a senior colleague explaining something to another technical person.
"""

class Agent:
    """Agent with multi-provider LLM support."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        debug: bool = False,
    ):
        provider_name = get_provider_name(provider)
        validate_provider_api_key(provider_name)
        prov = Provider(provider_name)
        selected_model = get_provider_model(provider_name, model)

        self.llm = LLMClient(LLMConfig(
            provider=prov,
            model=selected_model,
            system_prompt=SYSTEM_PROMPT,
        ))
        self.cost_tracker = CostTracker(model=selected_model)
        self.messages: list[dict] = []
        self.debug = debug
        self.console = Console()

    def _debug_step(self, step_type: str, content: str) -> None:
        if not self.debug:
            return

        self.console.print(Panel(
            content,
            title=f"[{step_type}]",
            border_style=DEBUG_STYLES[step_type],
        ))

    def chat(self, user_input: str, stream: bool = True) -> str:
        """Sends a message and returns the response."""
        self.messages.append({"role": "user", "content": user_input})
        iteration = self.cost_tracker.total_requests + 1
        self._debug_step(
            "THINKING",
            f"Iteration {iteration}: preparing a response for the latest user message.",
        )
        self._debug_step(
            "ACTION",
            f"Calling {self.llm.config.provider.value} model {self.llm.config.model} "
            f"({'streaming' if stream else 'complete'} mode).",
        )

        if stream:
            full_text = ""
            response_stream = self.llm.stream(self.messages)

            while True:
                try:
                    chunk = next(response_stream)
                    print(chunk, end="", flush=True)
                    full_text += chunk
                except StopIteration as finished:
                    response = finished.value
                    break

            print()
        else:
            response = self.llm.complete(self.messages)
            full_text = response.text

        request_cost = self.cost_tracker.track(response)
        self._debug_step(
            "RESULT",
            f"Iteration {iteration} completed: {response.input_tokens} input tokens, "
            f"{response.output_tokens} output tokens, estimated cost: "
            f"${request_cost:.6f}, stop reason: "
            f"{response.stop_reason or 'unknown'}.",
        )
        self.messages.append({
            "role": "assistant", "content": full_text
        })

        return full_text
