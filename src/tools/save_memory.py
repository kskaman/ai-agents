class SaveMemory:
    """
    Updates the agent's internal memory/scratchpad.
    """
    name = "save_memory"
    plan_safe = True
    description = "Updates your internal memory_scratchpad. " \
        "Use this to remember user preferences"
    input_schema = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The full text to save."
            }
        },
        "required": ["content"]
    }


    def execute(self, context, content):
        print(f"  -> Saving memory")
        if context.memory is None:
            return "Error: Memory not available"
        context.memory.save(content)
        return "Memory updated successfully"