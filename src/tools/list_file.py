import os

class ListFiles:
    """Lists files in the project structure."""
    name = "list_files"
    plan_safe = True
    description = "Lists all files in the project structure." \
        " Useful to understand the project layout."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The root path (default '.')"
            }
        }
    }

    def execute(self, context, path="."):
        print(f"  -> Listing {path}")

        try:
            file_list = []
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in {
                    ".git", "__pycache__", "venv", ".coding_agent"}]

                level = root.replace(path, '').count(os.sep)
                indent = ' ' * 4 * (level)
                file_list.append(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 4 * (level + 1)
                for f in files:
                    file_list.append(f"{sub_indent}{f}")

            return "\n".join(file_list)
        except Exception as e:
            return f"Error listing files: {e}"
