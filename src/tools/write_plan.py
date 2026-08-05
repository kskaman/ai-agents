class WritePlan:
    """Saves a plan to PLAN.md"""

    name = "write_plan"
    plan_safe = True
    description = "Saves a plan to PLAN.md." \
        "Use this to outline your approach before making changes."
    input_schema = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The plan content in markdown"
            },
        },
        "required": ["content"]
    }

    def execute(self, context, content):
        print(f"  -> Writing PLAN.md")

        try:
            with open("PLAN.md", "w", encoding='utf-8') as f:
                f.write(content)
            return "Plan saved to PLAN.md"
        except Exception as e:
            return f"Error writing PLAN.md: {e}"