"""
DSPy Modules for Charlie Munger RAG Agent
Streamlined DSPy integration with fallback support
"""

from .dspy_config import initialize_dspy, is_dspy_ready, get_dspy_status
from .simple_modules import (
    create_dspy_planner,
    create_dspy_synthesizer, 
    create_dspy_verifier
)

__all__ = [
    'initialize_dspy',
    'is_dspy_ready', 
    'get_dspy_status',
    'create_dspy_planner',
    'create_dspy_synthesizer',
    'create_dspy_verifier'
]
