import os

class SearchCodebase:
    """Searches for a string in all files."""

    name = "search_codebase"
    plan_safe = True
    description = "Searches the entire codebase for a text string." \
        " Useful to find where functions or variables are defined."

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The string to search for."
            },
            "path": {
                "type": "string",
                "description": "The root path (default '.')"
            },
        },
        "required": ["query"]
    }

    def execute(self, context, query, path="."):
        print(f"  -> Searching for '{query}'")

        results = []

        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in {
                    ".git", "__pycache__", "venv", ".coding_agent"
                }]

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8',
                            errors='ignore') as f:

                            for i, line in enumerate(f):
                                if query.lower() in line.lower():
                                    results.append(f"{file_path}:{i+1}:\
                                        {line.strip()}")
                    except Exception as e:
                        continue

            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Error searching: {e}"
                             