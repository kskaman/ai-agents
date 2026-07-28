"""Coding agent CLI entry point."""

import os
from dotenv import load_dotenv

from agent import Agent, AgentStop
from brain import Claude

# Load environment variables from .env file
load_dotenv()

    
def main():
    brain = Claude()
    agent = Agent(brain)

    print("CodeAgent v0.1 initialized.")
    print("Type '/q' to quit.")

    while True:
        try:
            user_input = input("> ")
            response = agent.handle_input(user_input)
            if response:
                print(f"\n{response}\n")

        except (AgentStop, KeyboardInterrupt):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()