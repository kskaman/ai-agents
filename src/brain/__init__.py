"""Brain module - LLM providers."""

from .brain import Brain
from .claude import Claude
from .deep_seek import DeepSeek
from .fake_brain import FakeBrain

# BRAINS Registry
# Available brains
BRAINS = {
    "claude": Claude,
    "deepseek": DeepSeek,
}

__all__ = ["Brain", "Claude", "DeepSeek", "FakeBrain", "BRAINS"]
