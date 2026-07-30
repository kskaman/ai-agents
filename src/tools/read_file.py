class ReadFile:
    """Reads a file from the filesystem."""

    name = "read_file"
    description = "Reads a file from the filesystem. Use this to examine code."

    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file"
            }
        },
        "required": ["path"]
    }

    def execute(self, path: str) -> str:
        print(f"  -> Reading {path}")

        try:
            with open(path, 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
                numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
                return "".join(numbered_lines)
        except Exception as e:
            return f"Error reading file: {e}"