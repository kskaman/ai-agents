"""Tests for the agent loop. The model is faked, so no network or API key."""

from task_operator.agent import react_loop
from task_operator.config import get_config
from tests.unit.fakes import FakeClient, response, text_block, tool_use_block


def test_loop_answers_without_tools():
    """If the model answers straight away, the loop returns that answer after
    a single API call."""
    client = FakeClient([response("end_turn", text_block("Hello!"))])
    assert react_loop("hi", verbose=False, client=client) == "Hello!"
    assert len(client.calls) == 1


def test_loop_runs_tool_and_feeds_result_back():
    """One full Reason -> Act -> Observe cycle: the model asks for a tool, the
    loop runs it, and the next request carries the result back, linked to
    the original tool call by its id."""
    client = FakeClient(
        [
            response("tool_use", tool_use_block("t1", "calculate", {"expression": "6 * 7"})),
            response("end_turn", text_block("The answer is 42.")),
        ]
    )
    assert react_loop("6*7?", verbose=False, client=client) == "The answer is 42."

    second_request = client.calls[1]["messages"]
    assert [m["role"] for m in second_request] == ["user", "assistant", "user"]
    [tool_result] = second_request[2]["content"]
    assert tool_result == {
        "type": "tool_result",
        "tool_use_id": "t1",
        "content": "42",
        "is_error": False,
    }


def test_loop_returns_parallel_tool_results_in_one_message():
    """When the model asks for two tools at once, both results go back together
    in a single message, in the same order."""
    client = FakeClient(
        [
            response(
                "tool_use",
                tool_use_block("a", "get_weather", {"city": "Tokyo"}),
                tool_use_block("b", "count_characters", {"text": "Tokyo"}),
            ),
            response("end_turn", text_block("done")),
        ]
    )
    react_loop("q", verbose=False, client=client)
    results = client.calls[1]["messages"][2]["content"]
    assert [r["tool_use_id"] for r in results] == ["a", "b"]


def test_loop_marks_tool_errors():
    """A tool that fails is sent back to the model flagged as an error
    (is_error=True), so the model knows the call didn't work."""
    client = FakeClient(
        [
            response("tool_use", tool_use_block("t1", "calculate", {"expression": "1/0"})),
            response("end_turn", text_block("Cannot divide by zero.")),
        ]
    )
    react_loop("1/0?", verbose=False, client=client)
    [tool_result] = client.calls[1]["messages"][2]["content"]
    assert tool_result["is_error"] is True


def test_loop_stops_at_max_iterations():
    """The safety valve: a model that keeps calling tools forever is cut off
    after max_iterations, and the loop returns an error instead of hanging."""
    looping = [response("tool_use", tool_use_block(f"t{i}", "count_characters", {"text": "x"}))
               for i in range(5)]
    client = FakeClient(looping)
    result = react_loop("loop forever", max_iterations=2, verbose=False, client=client)
    assert result == "Error: max iterations reached without a final answer."
    assert len(client.calls) == 2


def test_loop_reads_max_iterations_from_config(monkeypatch):
    """Without an explicit max_iterations, the loop uses the value from config
    (TASK_OPERATOR_MAX_ITERATIONS)."""
    monkeypatch.setenv("TASK_OPERATOR_MAX_ITERATIONS", "3")
    get_config.cache_clear()
    looping = [response("tool_use", tool_use_block(f"t{i}", "count_characters", {"text": "x"}))
               for i in range(5)]
    client = FakeClient(looping)
    react_loop("loop forever", verbose=False, client=client)
    assert len(client.calls) == 3


def test_loop_with_history_remembers_earlier_turns():
    """Passing the same history list to two calls makes the second request
    include the first question and answer - the agent's memory in chat."""
    client = FakeClient(
        [
            response("end_turn", text_block("It's 71°F in Tokyo.")),
            response("end_turn", text_block("About 21.7°C.")),
        ]
    )
    history = []
    react_loop("Weather in Tokyo?", verbose=False, client=client, history=history)
    react_loop("In Celsius?", verbose=False, client=client, history=history)

    second_request = client.calls[1]["messages"]
    assert [m["role"] for m in second_request] == ["user", "assistant", "user"]
    assert second_request[0]["content"] == "Weather in Tokyo?"
    assert second_request[2]["content"] == "In Celsius?"
    assert len(history) == 4  # both questions and both answers


def test_loop_handles_refusal():
    """If the model declines the request, the loop stops and says so."""
    client = FakeClient([response("refusal")])
    assert react_loop("x", verbose=False, client=client) == "Error: the model declined this request."
