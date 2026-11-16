"""Command-line entry point.

Run:  python -m task_operator "What is 15% of the temperature in Tokyo?"
"""

import sys

from task_operator.agent import react_loop
from task_operator.config import ConfigError, get_config

DEFAULT_TASK = (
    "What's the temperature in Tokyo in Celsius, and how many characters "
    "are in the word 'Tokyo'?"
)


def main() -> None:
    # Load and validate every env variable once, before doing any work, so a
    # bad .env fails here with a clear message. Later get_config() calls in
    # other modules reuse this cached result.
    try:
        get_config()
    except ConfigError as e:
        sys.exit(str(e))

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    print(f"\nFinal answer:\n{react_loop(task)}")


if __name__ == "__main__":
    main()
