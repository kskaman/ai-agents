import pytest

from task_operator import __main__ as entry


def test_arguments_are_rejected(monkeypatch):
    """Passing a question on the command line prints usage and exits,
    without starting the chat."""
    monkeypatch.setattr("sys.argv", ["task_operator", "What's the weather?"])
    monkeypatch.setattr(entry, "run_chat", lambda: pytest.fail("chat should not start"))
    with pytest.raises(SystemExit) as exc:
        entry.main()
    assert "No arguments" in str(exc.value)


def test_no_arguments_starts_chat(monkeypatch):
    """With no arguments, the chat starts."""
    started = []
    monkeypatch.setattr("sys.argv", ["task_operator"])
    monkeypatch.setattr(entry, "run_chat", lambda: started.append(True))
    entry.main()
    assert started == [True]
