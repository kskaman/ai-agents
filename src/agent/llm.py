import time
from dataclasses import dataclass
from enum import Enum
from typing import Generator

import anthropic
import openai

from openai import OpenAI

class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class LLMConfig:
    """LLM client configuration"""
    provider: Provider = Provider.ANTHROPIC
    model: str = "claude-sonnet-5"
    max_tokens: int = 4096
    temperature: float = 0.1
    max_retries: int = 3
    base_delay: float = 1.0
    system_prompt: str = ""


@dataclass
class LLMResponse:
    """Normalized response from any provider."""
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""


@dataclass
class CostTracker:
    """Tracks the accumulated cost of a session."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_requests: int = 0
    model: str = "claude-sonnet-5"

    PRICING = {
        "claude-sonnet-5": {"input": 3.00, "output": 15.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }

    def track(self, response: LLMResponse) -> None:
        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens
        self.total_requests += 1

    @property
    def total_cost(self) -> float:
        prices = self.PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        input_cost = (self.total_input_tokens / 1_000_000) * prices["input"]
        output_cost = (self.total_output_tokens / 1_000_000) * prices["output"]
        return input_cost + output_cost

    def summary(self) -> str:
        return (
            f"Requests: {self.total_requests} | "
            f"Tokens: {self.total_input_tokens} in / "
            f"{self.total_output_tokens} out | "
            f"Cost: ${self.total_cost:.4f}"
        )

class LLMClient:
    """Unified client for Anthropic and OpenAI."""

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()
        self._anthropic = None
        self._openai = None

    @property
    def anthropic_client(self) -> anthropic.Anthropic:
        if self._anthropic is None:
            self._anthropic = anthropic.Anthropic()
        return self._anthropic

    @property
    def openai_client(self) -> OpenAI:
        if self._openai is None:
            self._openai = OpenAI()
        return self._openai

    def complete(self, messages: list[dict]) -> LLMResponse:
        """Sends messages and returns the complete response."""
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                if self.config.provider == Provider.ANTHROPIC:
                    return self._complete_anthropic(messages)
                else:
                    return self._complete_openai(messages)
            except (
                anthropic.RateLimitError,
                anthropic.APITimeoutError,
                openai.RateLimitError,
                openai.APITimeoutError
            ) as e:
                last_error = e
                delay = self.config.base_delay * (2 ** attempt)
                time.sleep(delay)

            except (anthropic.APIStatusError, openai.APIStatusError) as e:
                if e.status_code >= 500:
                    last_error = e
                    delay = self.config.base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise e

        raise last_error

    def stream(self, messages: list[dict]) -> Generator[str, None, LLMResponse]:
        """Streams the response. Yields text, returns LLMResponse."""
        if self.config.provider == Provider.ANTHROPIC:
            return self._stream_anthropic(messages)
        else:
            return self._stream_openai(messages)

    def _complete_anthropic(self, messages: list[dict]) -> LLMResponse:
        response = self.anthropic_client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.config.system_prompt,
            messages=messages,
        )

        return LLMResponse(
            text=response.content[0].text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )

    def _complete_openai(self, messages: list[dict]) -> LLMResponse:
        oai_messages = []
        if self.config.system_prompt:
            oai_messages.append({
                "role": "system", 
                "content": self.config.system_prompt
            })

        oai_messages.extend(messages)

        response = self.openai_client.chat.completions.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=oai_messages,
        )

        choice = response.choices[0]

        return LLMResponse(
            text=choice.message.content,
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            stop_reason=choice.finish_reason,
        )


    def _stream_anthropic(
        self, 
        messages: list[dict]
    ) -> Generator[str, None, LLMResponse]:

        full_text = ""

        with self.anthropic_client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.config.system_prompt,
            messages=messages,
        ) as stream:

            for text in stream.text_stream:
                full_text += text
                yield text

        final = stream.get_final_message()

        return LLMResponse(
            text=full_text,
            model=final.model,
            input_tokens=final.usage.input_tokens,
            output_tokens=final.usage.output_tokens,
            stop_reason=final.stop_reason,
        )

    def _stream_openai(
        self,
        messages: list[dict]
    ) -> Generator[str, None, LLMResponse]:

        oai_messages = []

        if self.config.system_prompt:
            oai_messages.append({
                "role": "system", 
                "content": self.config.system_prompt
            })

        oai_messages.extend(messages)

        full_text = ""
        stream = self.openai_client.chat.completions.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=oai_messages,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                full_text += delta.content
                yield delta.content

        return LLMResponse(
            text=full_text,
            model=self.config.model,
            input_tokens=0,
            output_tokens=0,
            stop_reason=None,
        )
    