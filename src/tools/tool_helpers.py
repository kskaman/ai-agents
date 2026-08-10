import os

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


def resolve_path(path: str, workspace_dir: str) -> str:
    """
    Resolve a path to either workspace or agent codebase.
    
    Rules:
    - If path is absolute, use as-is
    - If path starts with 'src/', 'tests/', use agent codebase
    - If path is agent root file (coding_agent.py, requirements.txt, etc.), use agent codebase
    - Otherwise, use workspace/ directory for user projects
    
    Args:
        path: The path to resolve
        workspace_dir: The workspace directory (agent's root)
    
    Returns:
        The resolved absolute path
    """
    # Already absolute
    if os.path.isabs(path):
        return path
    
    # Normalize path separators
    normalized = os.path.normpath(path)
    
    # Agent code directory prefixes (must start with these)
    agent_dirs = ['src/', 'src\\']
    
    # Agent root files (exact filename match)
    agent_root_files = [
        'coding_agent.py',    # Main entry point
        'requirements.txt',   # Dependencies
        'README.md',          # Documentation
        'PLAN.md',           # Development plan
        'memory.md',         # Agent memory
        '.gitignore',        # Git config
        '.env'               # Environment config
    ]
    
    # Check if this is agent's own code
    is_agent_dir = any(normalized.startswith(d) for d in agent_dirs)
    is_agent_file = os.path.basename(normalized) in agent_root_files
    
    if is_agent_dir or is_agent_file:
        # Agent code: write to agent's root directory
        return os.path.join(workspace_dir, normalized)
    else:
        # User project: write to workspace/ subdirectory
        workspace_path = os.path.join(workspace_dir, "workspace")
        os.makedirs(workspace_path, exist_ok=True)
        return os.path.join(workspace_path, normalized)