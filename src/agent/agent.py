import os

"""Main agent implementation."""


class AgentStop(Exception):
    """Raised when the agent should stop processing."""
    pass


class Agent:
    """A coding agent that processes user input."""

    def __init__(self, brain, brain_name="claude"):
        self.brain = brain
        self.brain_name = brain_name
        self.conversation = []

    def handle_input(self, user_input):
        """
            Handle user input. Returns output string, 
            raises AgentStop to quit. 
        """

        if user_input.strip() == "/q":
            raise AgentStop("Agent stopped by user command.")

        if user_input.strip() == "/switch":
            return self._switch_brain()
        
        if not user_input.strip():
            return ""

        self.conversation.append({"role": "user", "content": user_input})

        try:
            thought = self.brain.think(self.conversation)
            if thought.thinking:
                lines = thought.thinking.strip().split("\n")[:5]

                for i, line in enumerate(lines):
                    prefix = "..." if i == 0 else "\t"
                    print(f"\033[2m{prefix}{line}\033[0m")

            text = thought.text or ""
            self.conversation.append({"role": "assistant", "content": text})
            return text
        except Exception as e:
            self.conversation.pop() # Remove failed user message
            return f"Error: {e}"

    def _switch_brain(self):
        """Switch between available brains."""
        from ..brain import BRAINS

        names = list(BRAINS.keys())

        idx = names.index(self.brain_name)

        new_name = names[(idx + 1) % len(names)]

        try:
            self.brain = BRAINS[new_name]()
            self.brain_name = new_name
            os.environ["BRAIN_NAME"] = new_name  # Update environment variable
            return f"Switched to: {new_name}"
        except ValueError as e:
            return f"Cannot switch to {new_name}: {e}"