"""Sound package — synthesis, effects, analysis, and generation.

Modular audio processing library for musicom.
"""

from . import synthesis
from . import effects
from . import analysis
from . import render
from . import generators
from . import utils

__all__ = [
    "synthesis",
    "effects",
    "analysis",
    "render",
    "generators",
    "utils",
]
