"""Interactive chat: talk to the agent turn by turn, with memory between turns."""

from __future__ import annotations

from collections.abc import Callable

from task_operator.agent import react_loop
from task_operator.brain import new_client

BANNER = "Task Operator - chat with the agent. /help for commands, /exit to quit."

HELP = """Commands:
  /help         show this help
  /reset        forget the conversation and start fresh
  /exit, /quit  leave the chat (Ctrl+C or Ctrl+D also work)"""


def run_chat(
    client=None,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> None:
    """Read a line, answer it, repeat. `read`/`write` are swappable for tests."""
    client = client or new_client()
    history: list = []
    write(BANNER)

    while True:
        try:
            line = read("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            write("\nBye!")
            return

        if not line:
            continue

        if line.startswith("/"):
            command = line.lower()
            if command in ("/exit", "/quit"):
                write("Bye!")
                return
            if command == "/reset":
                history.clear()
                write("Conversation cleared.")
                continue
            if command != "/help":
                write(f"Unknown command {line!r}.")
            write(HELP)
            continue

        turn_start = len(history)
        try:
            answer = react_loop(line, client=client, history=history)
        except KeyboardInterrupt:
            # Drop the half-finished turn: a tool call without its result
            # would make the next request invalid.
            del history[turn_start:]
            write("\n(interrupted - that turn was discarded)")
            continue
        except Exception as e:  # noqa: BLE001 - keep the chat alive on API errors
            del history[turn_start:]
            write(f"\nError: {type(e).__name__}: {e}")
            continue

        write(f"\nagent> {answer}")
