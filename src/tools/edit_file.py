class EditFile:
    """Replaces text in a file (surgical edit)"""

    name = "edit_file"
    plan_safe = False
    description = "Replaces specific text in a file." \
    "Use for surgical edits instead of rewriting entire files."

    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file"
            },
            "old_text": {
                "type": "string",
                "description": "Exact text to find and replace"
            },
            "new_text": {
                "type": "string",
                "description": "Text to replace it with",
            },
        },
        "required": ["path", "old_text", "new_text"],
    }

    def execute(self, context, path, old_text, new_text):
        print(f"  -> Editing file: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if old_text not in content:
                return f"Error: Could not find the specified text in {path}"

            new_content = content.replace(old_text, new_text, 1)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return f"Successfully replaced text in {path}"
        except Exception as e:
            return f"Error editing file: {e}"