"""Tool: text utilities."""


def count_characters(text: str) -> str:
    """Count the characters in a string."""
    return str(len(text))


SCHEMA = {
    "name": "count_characters",
    "description": "Count the number of characters in a piece of text, including spaces.",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The text to count."}
        },
        "required": ["text"],
    },
}
