from .llm import LLMClient, LLMConfig, Provider

SYSTEM_PROMPT = """You are Aria, an AI agent for research and task
execution.

## Behavior
- Be direct and to the point. Avoid beating around the bush.
- When you don't know something, say so clearly instead of making things up.
- Prefer structured responses with lists and sections when appropriate.

## Tone
- Professional but approachable.
- Like a senior colleague explaining something to another technical person.
"""

class Agent:
    """Aria agent with multi-provider LLM support."""

    def __init__(self, provider: str = "anthropic"):
        prov = Provider(provider)

        model = (
            "claude-sonnet-5"
            if prov == Provider.ANTHROPIC
            else "gpt-4o"
        )

        self.llm = LLMClient(LLMConfig(
            provider=prov,
            model=model,
            system_prompt=SYSTEM_PROMPT,
        ))

        self.messages: list[dict] = []

    def chat(self, user_input: str, stream: bool = True) -> str:
        """Sends a message and returns the response."""
        self.messages.append({"role": "user", "content": user_input})

        if stream:
            full_text = ""

            for chunk in self.llm.stream(self.messages):
                print(chunk, end="", flush=True)
                full_text += chunk
                print()
        else:
            response = self.llm.complete(self.messages)
            full_text = response.text
            self.messages.append({
                "role": "assistant", "content": full_text
            })

        return full_text
