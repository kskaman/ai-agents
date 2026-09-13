"""src/aria/cli.py — Aria interactive CLI."""
from dotenv import load_dotenv
from .agent import Agent

load_dotenv()

def main():
    agent = Agent()

    print("Agent v0.2 — type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        print("\nAgent: ", end="")
        agent.chat(user_input)
        print()

if __name__ == "__main__":
    main()
