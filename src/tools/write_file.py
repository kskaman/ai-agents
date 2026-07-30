class WriteFile:
    """Writes content to a file."""

    name = "write_file"
    description = "Writes content to a file. OVERWRITES existing content."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file"
            },
            "content": {
                "type": "string",
                "description": "The full content to write"
            }
        },
        "required": ["path", "content"]
    }

    def execute(self, path: str, content: str) -> str:
        print(f"  -> Writing to {path}")

        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully wrote to {len(content)} characters to {path}"
        except Exception as e:
            return f"Error writing to file: {e}"