"""Coding agent CLI entry point."""

import os
from dotenv import load_dotenv

from src.agent import Agent, AgentStop
from src.brain import BRAINS
from src.tools import tools, tool_definitions

# Load environment variables from .env file
load_dotenv()

    
def main():
    brain_name = os.getenv("BRAIN_NAME")
    brain = BRAINS[brain_name](tools=tool_definitions(tools))
    agent = Agent(brain, tools=tools, brain_name=brain_name)

    print("CodeAgent v0.1")
    print("Commands:\n\t'/q' - quit\n\t'/switch' - switch brain\n")
    

    while True:
        try:
            user_input = input(f"[{agent.brain_name}] > ")
            response = agent.handle_input(user_input)
            if response:
                print(f"\n{response}\n")

        except (AgentStop, KeyboardInterrupt):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()