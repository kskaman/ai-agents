"""Tests for the chat CLI. Keyboard input is scripted and the model is faked."""

from task_operator.cli.chat import run_chat
from tests.unit.fakes import FakeClient, response, text_block


def scripted(lines):
    """Pretend to be input(): return each line in turn, then act like Ctrl+D."""
    remaining = iter(lines)

    def read(_prompt):
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError from None

    return read


def chat(lines, replies=()):
    """Run a chat with scripted input; return (everything printed, fake client)."""
    client = FakeClient([response("end_turn", text_block(r)) for r in replies])
    output = []
    run_chat(client=client, read=scripted(lines), write=output.append)
    return "\n".join(output), client


def test_chat_answers_and_remembers_between_turns():
    """Two questions in a row: both answers are shown, and the second request
    to the model includes the first question and answer."""
    output, client = chat(["Weather in Tokyo?", "In Celsius?", "/exit"],
                          replies=["71°F.", "About 21.7°C."])
    assert "agent> 71°F." in output
    assert "agent> About 21.7°C." in output
    assert len(client.calls[1]["messages"]) == 3


def test_reset_forgets_the_conversation():
    """After /reset, the next question is sent with no earlier messages."""
    output, client = chat(["Hi", "/reset", "Hi again", "/exit"], replies=["Hello!", "Hello again!"])
    assert "Conversation cleared." in output
    assert len(client.calls[1]["messages"]) == 1


def test_exit_and_quit_end_the_chat():
    """/exit and /quit stop the chat before any later lines are read."""
    for command in ("/exit", "/quit"):
        output, client = chat([command, "this is never sent"])
        assert "Bye!" in output
        assert client.calls == []


def test_ctrl_d_ends_the_chat():
    """Running out of input (Ctrl+D) exits cleanly instead of crashing."""
    output, _ = chat([])
    assert "Bye!" in output


def test_blank_lines_are_ignored():
    """Pressing Enter on an empty line doesn't call the model."""
    _, client = chat(["", "   ", "/exit"])
    assert client.calls == []


def test_unknown_command_shows_help_without_calling_model():
    """A mistyped command prints a hint and the help text, and isn't sent
    to the model as a question."""
    output, client = chat(["/weather", "/exit"])
    assert "Unknown command '/weather'" in output
    assert "/reset" in output
    assert client.calls == []


def test_api_error_keeps_chat_alive_and_discards_the_turn():
    """If the model call fails, the error is printed, the chat continues, and
    the failed question is not left in memory."""
    client = FakeClient([ConnectionError("network down"),
                         response("end_turn", text_block("Hello!"))])
    output = []
    run_chat(client=client, read=scripted(["Hi", "Hi again", "/exit"]), write=output.append)
    text = "\n".join(output)
    assert "Error: ConnectionError: network down" in text
    assert "agent> Hello!" in text
    # The failed "Hi" was dropped, so the retry is sent on its own.
    assert client.calls[1]["messages"] == [{"role": "user", "content": "Hi again"}]
