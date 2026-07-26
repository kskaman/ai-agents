# -- Exceptions --

class AgentStop(Exception):
    """Raised when the agent should stop processing."""
    pass


class Agent:
    """A coding agent that processes user input."""

    def __init__(self):
        pass

    def handle_input(self, user_input):
        """
            Handle user input. Returns output string, 
            raises AgentStop to quit. 
        """

        if user_input.strip() == "/q":
            raise AgentStop("Agent stopped by user command.")

        if not user_input.strip():
            return ""

        return f"You said: {user_input}\n(Agent not yet connected)"



def main():
    agent = Agent()
    print("CodeAgent v0.1 initialized.")
    print("Type '/q' to quit.")

    while True:
        try:
            user_input = input("\n> ")
            response = agent.handle_input(user_input)
            if response:
                print(response)

        except (AgentStop, KeyboardInterrupt):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()