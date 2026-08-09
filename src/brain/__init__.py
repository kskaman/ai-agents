"""Brain module - LLM providers."""

from .brain import Brain
from .claude import Claude
from .deep_seek import DeepSeek
from .fake_brain import FakeBrain
from .ollama import Ollama

# BRAINS Registry
# Available brains
BRAINS = {
    "claude": Claude,
    "deepseek": DeepSeek,
    "ollama": Ollama,
}

__all__ = ["Brain", "Claude", "DeepSeek",
           "Ollama", "FakeBrain", "BRAINS"]
