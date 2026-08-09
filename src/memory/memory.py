import os

class Memory:
    """
    Persistent scratchpad for the agent."""

    def __init__(self, path="memory.md"):
        self.path = path
        self._ensure_exists()
        self.content = self._load()

    def _ensure_exists(self):
        """Create memory file with default content if needed."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            default = "I am Coding Agent, a helpful coding assistant.\n"
            with open(self.path, "w") as f:
                f.write(default)

    def _load(self):
        """Load memory content from file."""
        with open(self.path, "r") as f:
            return f.read()


    def save(self, content):
        """Update memory content and persist to disk."""
        self.content = content
        with open(self.path, "w") as f:
            f.write(content)
