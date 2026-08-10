import os
from .tool_helpers import resolve_path

class WriteFile:
    """Writes content to a file."""

    name = "write_file"
    plan_safe = False
    description = (
        "Writes content to a file. OVERWRITES existing content. "
        "User projects go to workspace/ folder automatically. "
        "Agent code (src/, src/tests/, coding_agent.py, etc.) can be modified directly."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file (relative to workspace, or use 'src/' for agent code)"
            },
            "content": {
                "type": "string",
                "description": "The full content to write"
            }
        },
        "required": ["path", "content"]
    }

    def execute(self, context, path: str, content: str) -> str:
        resolved_path = resolve_path(path, context.workspace_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        
        print(f"  -> Writing to {resolved_path}")

        try:
            with open(resolved_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully wrote {len(content)} characters to {resolved_path}"
        except Exception as e:
            return f"Error writing to file: {e}"