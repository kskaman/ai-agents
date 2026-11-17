"""A fake Anthropic client plus helpers to build scripted model responses.

Lets agent tests run the real loop with no network and no API key.
"""

from types import SimpleNamespace


def text_block(text):
    return SimpleNamespace(type="text", text=text)


def tool_use_block(id_, name, input_):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=input_)


def response(stop_reason, *content):
    return SimpleNamespace(stop_reason=stop_reason, content=list(content))


class FakeClient:
    """Mimics client.beta.messages.create and records every request.

    Each item in `responses` is returned in turn; an Exception item is raised
    instead, to simulate an API error.
    """

    def __init__(self, responses):
        self._responses = iter(responses)
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        # Snapshot the history: the loop keeps mutating the same list.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        result = next(self._responses)
        if isinstance(result, Exception):
            raise result
        return result
