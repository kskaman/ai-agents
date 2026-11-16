"""Command-line entry point.

Run:  python -m task_operator "What is 15% of the temperature in Tokyo?"
"""

import sys

from task_operator.agent import react_loop
from task_operator.brain import new_client
from task_operator.config import ConfigError, get_config

DEFAULT_TASK = (
    "What's the temperature in Tokyo in Celsius, and how many characters "
    "are in the word 'Tokyo'?"
)


def main() -> None:
    # Load and validate every env variable once, before doing any work.
    # Done only here (not at import) so unit tests never pick up a real key.
    try:
        config = get_config()
    except ConfigError as e:
        sys.exit(str(e))

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    answer = react_loop(
        task,
        max_iterations=config["TASK_OPERATOR_MAX_ITERATIONS"],
        verbose=config["TASK_OPERATOR_VERBOSE"],
        client=new_client(api_key=config["ANTHROPIC_API_KEY"]),
    )
    print(f"\nFinal answer:\n{answer}")


if __name__ == "__main__":
    main()
