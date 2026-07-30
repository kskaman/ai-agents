def get_tool(tools, name):
    """Find a tool by name, or None if not found."""
    return next((tool for tool in tools if tool.name == name), None)


def tool_definitions(tools):
    """Return tool definitions for the API."""
    return [
        {
            "name": tool.name, 
            "description": tool.description, 
            "input_schema": tool.input_schema
        } for tool in tools
    ]