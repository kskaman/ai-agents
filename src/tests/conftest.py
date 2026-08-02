"""pytest configuration for test suite."""
import sys
from pathlib import Path

# Add the parent directory (project root) to the Python path
# This allows imports like: from src.agent import Agent
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
