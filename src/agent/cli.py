"""RTE interactive CLI."""
import argparse

from config.env_config import EnvironmentConfigError
from .agent import Agent

def print_help():
    print("""Commands:
    \n\t(/exit, /quit) - exit the CLI
    \n\t/cost - show the current session cost summary
    \n\t/help - show this help message
    \n""") 


def main():
    parser = argparse.ArgumentParser(
        prog="rte",
        description="Research and task execution agent.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show each step of the agent loop.",
    )
    parser.add_argument(
        "--provider",
        choices=("anthropic", "openai"),
        help="LLM provider (defaults to PROVIDER or anthropic).",
    )
    parser.add_argument(
        "--model",
        help="Model override (defaults to the provider's model environment variable).",
    )
    args = parser.parse_args()

    try:
        agent = Agent(provider=args.provider, model=args.model, debug=args.debug)
    except EnvironmentConfigError as error:
        parser.exit(2, f"Configuration error: {error}\n")

    print("Agent v0.2 — type 'exit' to quit.\n")
    print_help()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in ("/exit", "/quit"):
            print("Exiting...")
            break

        if command == "/cost":
            print(agent.cost_tracker.summary())
            continue

        if command == "/help":
            print_help()
            continue

        if user_input.startswith("/"):
            print(f"Unknown command: {user_input}")
            continue

        print("\nAgent: ", end="")
        agent.chat(user_input)
        

if __name__ == "__main__":
    main()
