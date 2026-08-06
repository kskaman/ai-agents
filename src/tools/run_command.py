import os
import subprocess

class RunCommand:
    """Executes shell commands."""
    name = "run_command"
    plan_safe = False
    description = "Executes a terminal command. Use this " \
    "to run scripts, tests, or install packages."
    input_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to run (e.g., 'python test.py')",
            },
        },
        "required": ["command"],
    }

    def execute(self, context, command):
        print(f"  -> Running: {command[:50]}...")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=int(os.environ.get("CODING_AGENT_TIMEOUT", "30")),
                cwd=os.getcwd()
            )

            output = ""

            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            if not output:
                output = "(No output)"

            return output.strip()

        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"Error executing command: {e}"