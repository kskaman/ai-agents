"""Coding agent CLI entry point."""

import os
import sys

from dotenv import load_dotenv

from src.agent import Agent, AgentStop
from src.brain import BRAINS
from src.tools import tools
from src.memory import Memory

# Load environment variables from .env file
load_dotenv()

    
def main():
    # Parse mode from CLI
    mode = "act" if len(sys.argv) > 1 and \
        sys.argv[1] == "--act" else "plan"

    brain_name = os.getenv("BRAIN_NAME")

    memory = Memory()

    brain = BRAINS[brain_name](memory=memory)

    agent = Agent(brain, tools=tools, 
        memory=memory, mode=mode, brain_name=brain_name)

    print("Coding Agent v0.6")
    print("Commands: /q quit, /switch toggle brain, /mode [plan|act], /reset clear history")
    print(f"Brain: {agent.brain_name}")
    
    if mode == "act":
        print("Mode: ACT (Writing Enabled)")
    else:
        print("Mode: PLAN (Code Read-Only)")
    
    print()  # Empty line before prompt

    while True:
        try:
            user_input = input(f"[{agent.brain_name}:{agent.mode}] ❯ ")
            
            try:
                response = agent.handle_input(user_input)
                if response:
                    print(f"\n{response}\n")
            except KeyboardInterrupt:
                print("\n\n Query interrupted. Press Ctrl+C again at prompt to exit.\n")
                continue

        except (AgentStop, KeyboardInterrupt):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()