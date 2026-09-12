import argparse

from .agent import run_agent

def main():
    """Interactive command-line interface for the agent."""
    parser = argparse.ArgumentParser(prog="rte", description="Research and task execution agent.")
    parser.add_argument("--debug", action="store_true", help="Show each step of the agentic loop.")
    args = parser.parse_args()

    print("rte v0.1 - type 'exit' to quit.\n")

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

        response = run_agent(user_input, debug=args.debug)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()