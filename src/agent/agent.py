import os
from ..tools import get_tool, tool_definitions, ToolContext

"""Main agent implementation."""


class AgentStop(Exception):
    """Raised when the agent should stop processing."""
    pass


class Agent:
    """A coding agent that processes user input."""

    def __init__(self, brain, tools, memory = None,
        mode="plan", brain_name="claude", workspace_dir=None):
        self.brain = brain
        self.memory = memory
        self.mode = mode
        self.tools = list(tools)
        self.workspace_dir = workspace_dir or os.getcwd()

        # User-created projects live here unless a path targets agent source.
        os.makedirs(os.path.join(self.workspace_dir, "workspace"), exist_ok=True)

        self.brain_name = brain_name
        self.brain.tools = self._tools_for_mode()
        self.brain.system = self._build_system_prompt()
        self.conversation = []


    def _build_system_prompt(self):
        """Build system prompt from memory and current mode."""
        parts = [
            "You are a direct, efficient coding assistant.",
            "When asked to do something simple, just do it - don't overthink or explore first.",
            "Examples:",
            "  - 'run tests' → immediately run pytest, don't read test files first",
            "  - 'list files' → immediately list, don't analyze structure",
            "  - 'fix bug' → read the file, fix it, done",
            "Only gather context when you truly need it to complete the task.",
            "",
            "WORKSPACE: User projects are stored in workspace/ folder by default.",
            "  - Writing 'app.py' creates workspace/app.py",
            "  - Reading 'config.json' reads workspace/config.json",
            "  - To modify agent code, use paths like 'src/*' or 'coding_agent.py'",
            "  - To read agent tests, use path 'src/tests/test_agent.py'"
        ]
        if self.memory:
            parts.append("\n" + self.memory.content)
        if self.mode == "plan":
            parts.append(
                "\nYou are in PLAN mode. You cannot write code files. "
                "Use write_plan to save your plans to PLAN.md."
            )
        return "\n".join(parts)


    def _tools_for_mode(self):
        """Return tool definitions based on the current mode."""
        if self.mode == "act":
            return tool_definitions(self.tools)
        return tool_definitions([t for t in self.tools if t.plan_safe])

    

    def handle_input(self, user_input):
        """
            Handle user input. Returns output string, 
            raises AgentStop to quit. 
        """

        if user_input.strip() == "/q":
            raise AgentStop("Agent stopped by user command.")

        if user_input.strip().startswith("/switch"):
            return self._handle_switch_command(user_input)

        if user_input.strip().startswith("/mode"):
            return self._handle_mode_command(user_input)
        
        if user_input.strip() == "/reset":
            return self._reset_conversation()
            
        if not user_input.strip():
            return ""

        self.conversation.append({"role": "user", "content": user_input})

        try:
            return self._agentic_loop()
        except Exception as e:
            self.conversation.pop() # Remove failed user message
            return f"Error: {e}"


    def _handle_mode_command(self, user_input):
        """Handle /mode command to switch between plan and act."""
        parts = user_input.strip().split()

        if len(parts) > 1 and parts[1] == "act":
            self.mode = "act"
            self.brain.tools = self._tools_for_mode()
            self.brain.system = self._build_system_prompt()
            return "Switched to ACT mode (Writing Enabled)"
        else:
            self.mode = "plan"
            self.brain.tools = self._tools_for_mode()
            self.brain.system = self._build_system_prompt()
            return "Switched to PLAN mode (Code Read-Only)"

    
    def _reset_conversation(self):
        """Reset conversation history to clear broken state."""
        self.conversation = []
        return "Conversation history cleared"

    
    def _handle_switch_command(self, user_input):
        """Handle /switch command to select or cycle brain providers."""
        parts = user_input.strip().split()
        if len(parts) > 2:
            return "Usage: /switch [claude|deepseek|ollama]"

        return self._switch_brain(parts[1] if len(parts) == 2 else None)


    def _switch_brain(self, target_name=None):
        """Switch to a selected brain, or cycle to the next one."""
        from ..brain import BRAINS

        names = list(BRAINS.keys())

        if target_name is None:
            idx = names.index(self.brain_name)
            new_name = names[(idx + 1) % len(names)]
        else:
            new_name = target_name.lower()
            if new_name not in BRAINS:
                return f"Unknown brain '{target_name}'. Available brains: {', '.join(names)}"

        if new_name == self.brain_name:
            return f"Already using: {new_name}"

        try:
            self.brain = BRAINS[new_name](memory=self.memory, tools=self._tools_for_mode())
            self.brain_name = new_name
            self.brain.system = self._build_system_prompt()
            os.environ["BRAIN_NAME"] = new_name  # Update environment variable
            return f"Switched to: {new_name}"
        except ValueError as e:
            return f"Cannot switch to {new_name}: {e}"


    def _agentic_loop(self):
        """Process brain responses, executing tools until done."""

        output_parts = []
        max_iterations = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
        iteration = 0

        while True:
            iteration += 1
            if iteration > max_iterations:
                output_parts.append(f"\n  Reached max iterations ({max_iterations}).")
                break

            try:
                thought = self.brain.think(self.conversation)
            except KeyboardInterrupt:
                print("\n\nAgent interrupted by user (Ctrl+C)")
                # Remove last assistant message if present
                if self.conversation and self.conversation[-1]["role"] == "assistant":
                    self.conversation.pop()
                return "\n".join(output_parts) + "\n\nInterrupted by user"

            # Compact if approaching context limit
            if self.brain.last_input_tokens > self.brain.context_limit * 0.75:
                self._compact_conversation()

            # Store provider content for message history. Claude thinking blocks
            # must keep their signatures when extended thinking is enabled.
            self.conversation.append({
                "role": "assistant", 
                "content": thought.raw_content or [{"type": "text", "text": thought.text or ""}]
            })

            # Collect text output
            if thought.text:
                output_parts.append(thought.text)
                
            # Check for tool calls
            if not thought.tool_calls:
                break

            # Executes tools and collect results
            tool_results = []
            try:
                for tool_call in thought.tool_calls:
                    print(f"\n[Tool Use: {tool_call.name}]")
                    result = self._execute_tool(tool_call.name, tool_call.args)
                    print(f"[Tool Output: {result[:80]}...]" if len(result) > 80 else f"[Tool Output: {result}]")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result
                    })
            except KeyboardInterrupt:
                print("\n\nAgent interrupted by user (Ctrl+C)")
                # Remove last assistant message if present
                if self.conversation and self.conversation[-1]["role"] == "assistant":
                    self.conversation.pop()
                return "\n".join(output_parts) + "\n\nInterrupted by user"

            self.conversation.append({
                "role": "user",
                "content": tool_results
            })

        if getattr(self.brain, "streams_output", False):
            return ""

        return "\n".join(output_parts)


    def _execute_tool(self, tool_name, args):
        """Execute a tool by name with given arguments."""
        tool = get_tool(self.tools, tool_name)

        if tool is None:
            return f"Error : Tool '{tool_name}' not found."

        try:
            context = ToolContext(memory=self.memory, workspace_dir=self.workspace_dir)
            return tool.execute(context, **args)
        except TypeError as e:
            return f"Error: Invalid arguments - {e}"


    def _compact_conversation(self):
        """Summarize old messages to stay within context limits."""
        print("(compacting conversation...)")

        history = "\n".join(
            f"{m['role']}: {str(m['content'])[:500]}"
            for m in self.conversation
        )

        prompt = [{
            "role": "user",
            "content": f"Summarize this conversation for continuity. "
                       f"Focus on what was accomplished, what's in progress, "
                       f"and key decisions:\n\n{history}"
        }]

        saved_tools = self.brain.tools
        self.brain.tools = []
        try:
            thought = self.brain.think(prompt)
        finally:
            self.brain.tools = saved_tools

        self.conversation = [{
            "role": "user",
            "content": f"Previous conversation summary: {thought.text}"
        }]
