"""The model call. This is the only module that talks to the Anthropic API."""

from __future__ import annotations

import anthropic

from task_operator.brain.prompts import SYSTEM_PROMPT

# Pinned in one place so a model change is a one-line, reviewable diff.
# The book uses a Sonnet model; swap to "claude-sonnet-5-5" for a cheaper run.
MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000


def new_client(api_key: str | None = None) -> anthropic.Anthropic:
    """Create an API client (falls back to ANTHROPIC_API_KEY in the environment)."""
    return anthropic.Anthropic(api_key=api_key)


def think(client, messages: list, tools: list, system: str = SYSTEM_PROMPT):
    """One Reason step: send the conversation so far, get the model's next move."""
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        tools=tools,
        messages=messages,
        # "summarized" returns a readable summary of the model's reasoning,
        # so we can print the Thought step. Thinking itself is always on.
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": "medium"},
        # If a safety classifier declines, the API retries on a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
