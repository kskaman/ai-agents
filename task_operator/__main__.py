"""Command-line entry point: starts the chat.

Run:  python -m task_operator
"""

import sys

from task_operator.cli import run_chat
from task_operator.config import ConfigError, get_config

USAGE = "Usage: python -m task_operator\n(No arguments - ask your questions inside the chat.)"


def main() -> None:
    if len(sys.argv) > 1:
        sys.exit(USAGE)

    # Load and validate every env variable once, before doing any work, so a
    # bad .env fails here with a clear message. Later get_config() calls in
    # other modules reuse this cached result.
    try:
        get_config()
    except ConfigError as e:
        sys.exit(str(e))

    run_chat()


if __name__ == "__main__":
    main()
