from .tool_helpers import resolve_path

class ReadFile:
    """Reads a file from the filesystem."""

    name = "read_file"
    plan_safe = True
    description = (
        "Reads a file from the filesystem. Use this to examine code. "
        "By default, reads from workspace/ folder. "
        "To read agent code, use paths like 'src/*'."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file (relative to workspace, or use 'src/' for agent code)"
            }
        },
        "required": ["path"]
    }

    def execute(self, context, path: str) -> str:
        resolved_path = resolve_path(path, context.workspace_dir)
        print(f"  -> Reading {resolved_path}")

        try:
            with open(resolved_path, 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
                numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
                return "".join(numbered_lines)
        except Exception as e:
            return f"Error reading file: {e}"