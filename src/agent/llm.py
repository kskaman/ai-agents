import time
from dataclasses import dataclass
from enum import Enum
from typing import Generator

import anthropic
import openai

from config.env_config import get_env_float
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
    accumulated_cost: float = 0.0
    model: str = "claude-sonnet-5"

    PRICING = {
        "claude-sonnet-5": {"input": 3.00, "output": 15.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    def _prices_for(self, model: str) -> dict[str, float]:
        price_model = model if model in self.PRICING else next(
            (
                name
                for name in sorted(self.PRICING, key=len, reverse=True)
                if model.startswith(f"{name}-")
            ),
            self.model,
        )
        defaults = self.PRICING.get(price_model, {"input": 3.0, "output": 15.0})
        model_key = "".join(
            character if character.isalnum() else "_"
            for character in price_model
        ).upper()

        return {
            token_type: get_env_float(
                f"PRICE_{model_key}_{token_type.upper()}_PER_MILLION",
                default,
            )
            for token_type, default in defaults.items()
        }

    def _cost_for(self, response: LLMResponse) -> float:
        prices = self._prices_for(response.model)

        input_cost = (response.input_tokens / 1_000_000) * prices["input"]
        output_cost = (response.output_tokens / 1_000_000) * prices["output"]
        return input_cost + output_cost

    def track(self, response: LLMResponse) -> float:
        request_cost = self._cost_for(response)
        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens
        self.total_requests += 1
        self.accumulated_cost += request_cost
        return request_cost

    @property
    def total_cost(self) -> float:
        return self.accumulated_cost

    def summary(self) -> str:
        return (
            f"Requests: {self.total_requests} | "
            f"Tokens: {self.total_input_tokens} in / "
            f"{self.total_output_tokens} out | "
            f"Estimated cost: ${self.total_cost:.4f}"
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
            self._anthropic = anthropic.Anthropic(max_retries=0)
        return self._anthropic

    @property
    def openai_client(self) -> OpenAI:
        if self._openai is None:
            self._openai = OpenAI(max_retries=0)
        return self._openai

    def complete(self, messages: list[dict]) -> LLMResponse:
        """Sends messages and returns the complete response."""
        for attempt in range(max(1, self.config.max_retries)):
            try:
                if self.config.provider == Provider.ANTHROPIC:
                    return self._complete_anthropic(messages)
                return self._complete_openai(messages)
            except Exception as error:
                if not self._should_retry(error, attempt):
                    raise
                self._wait_before_retry(attempt)

    def stream(self, messages: list[dict]) -> Generator[str, None, LLMResponse]:
        """Streams the response. Yields text, returns LLMResponse."""
        for attempt in range(max(1, self.config.max_retries)):
            response_stream = (
                self._stream_anthropic(messages)
                if self.config.provider == Provider.ANTHROPIC
                else self._stream_openai(messages)
            )
            emitted_text = False

            try:
                while True:
                    try:
                        chunk = next(response_stream)
                    except StopIteration as finished:
                        return finished.value

                    emitted_text = True
                    yield chunk
            except Exception as error:
                if emitted_text or not self._should_retry(error, attempt):
                    raise
                self._wait_before_retry(attempt)

        raise RuntimeError("LLM stream retry loop ended unexpectedly")

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        if attempt + 1 >= max(1, self.config.max_retries):
            return False

        if isinstance(error, (
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
        )):
            return True

        if isinstance(error, (anthropic.APIStatusError, openai.APIStatusError)):
            return error.status_code >= 500

        return False

    def _wait_before_retry(self, attempt: int) -> None:
        delay = self.config.base_delay * (2 ** attempt)
        time.sleep(delay)

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
        with self.openai_client.chat.completions.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=oai_messages,
            stream_options={"include_usage": True},
        ) as stream:
            for event in stream:
                if event.type == "content.delta":
                    full_text += event.delta
                    yield event.delta

            final = stream.get_final_completion()

        usage = final.usage
        choice = final.choices[0]

        return LLMResponse(
            text=full_text,
            model=final.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            stop_reason=choice.finish_reason,
        )
    