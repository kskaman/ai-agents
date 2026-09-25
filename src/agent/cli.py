"""RTE interactive CLI."""
import argparse

from dotenv import load_dotenv
from .agent import Agent

load_dotenv()

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
    args = parser.parse_args()

    agent = Agent(debug=args.debug)

    print("Agent v0.2 — type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Exiting...")
            break

        print("\nAgent: ", end="")
        agent.chat(user_input)
        print(agent.cost_tracker.summary())
        

if __name__ == "__main__":
    main()
