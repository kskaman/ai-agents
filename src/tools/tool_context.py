import os

class ToolContext:
    """
    What tools need to know about the agent's state
    """

    def __init__(self, memory=None, workspace_dir=None):
        self.memory = memory
        self.workspace_dir = workspace_dir or os.path.join(os.getcwd(), "workspace")