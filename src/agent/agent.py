import os
from ..tools import get_tool, tool_definitions, ToolContext

"""Main agent implementation."""


class AgentStop(Exception):
    """Raised when the agent should stop processing."""
    pass


class Agent:
    """A coding agent that processes user input."""

    def __init__(self, brain, tools, memory = None, brain_name="claude"):
        self.brain = brain
        self.memory = memory
        self.tools = list(tools)
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
            return self._agentic_loop()
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
            self.brain = BRAINS[new_name](memory=self.memory, tools=tool_definitions(self.tools))
            self.brain_name = new_name
            os.environ["BRAIN_NAME"] = new_name  # Update environment variable
            return f"Switched to: {new_name}"
        except ValueError as e:
            return f"Cannot switch to {new_name}: {e}"


    def _agentic_loop(self):
        """Process brain responses, executing tools until done."""

        output_parts = []

        while True:
            thought = self.brain.think(self.conversation)

            # Display Thinking
            if thought.thinking:
                lines = thought.thinking.strip().split("\n")[:5]

                for i, line in enumerate(lines):
                    prefix = "..." if i == 0 else "\t"
                    print(f"\033[2m{prefix}{line}\033[0m")

            # Store raw content for message history (Claude expects this format)
            self.conversation.append({
                "role": "assistant", 
                "content": thought.raw_content
            })

            # Collect text output
            if thought.text:
                output_parts.append(thought.text)
                
            # Check for tool calls
            if not thought.tool_calls:
                break

            # Executes tools and collect results
            tool_results = []
            for tool_call in thought.tool_calls:

                result = self._execute_tool(tool_call.name, tool_call.args)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                })

            self.conversation.append({
                "role": "user",
                "content": tool_results
            })

        return "\n".join(output_parts)


    def _execute_tool(self, tool_name, args):
        """Execute a tool by name with given arguments."""
        tool = get_tool(self.tools, tool_name)

        if tool is None:
            return f"Error : Tool '{tool_name}' not found."

        try:
            context = ToolContext(memory=self.memory)
            return tool.execute(context, **args)
        except TypeError as e:
            return f"Error: Invalid arguments - {e}"