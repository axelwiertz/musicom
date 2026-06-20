"""
Musicom - Music Composition Library
A Python library for algorithmic music composition, analysis, and generation.

Main modules:
- structures: Core music data structures (MusicUnit, MusicVoice, MusicSection, etc.)
- converters: Conversion between different music formats
- generators: Music generation algorithms
- rules: Music theory rules and harmony
- utilities: Helper utilities and configuration
- ai: AI-driven generators, I/O, and library integration bridge
"""

__version__ = '0.1.0'
__author__ = 'Musicom Team'


# Core structures
from .structures import (
    # Music structures
    MusicUnit,
    MusicVoice,
    MusicSection,
    MusicProject,

    # Music theory
    MusicPitchClass,
    MusicPitchClassSet,
    MusicPitchClassSet,  # Backward compatibility alias
    PatternGraph,

    # Rhythm
    MusicTimeGrid,
    MusicRhythmPattern,
)


# Generators
from .generators import (
    PatternGenerator
)
# Configuration
from .utilities.config import Config

__all__ = [
    # Version info
    '__version__',
    '__author__',

    # Core structures
    'MusicUnit',
    'MusicVoice',
    'MusicSection',
    'MusicProject',

    # Pitch
    'MusicPitchClass',
    'MusicPitchClassSet',
    'MusicPitchClassSet',  # Backward compatibility
    'PatternGraph',

    # Time
    'MusicTimeGrid',
    # Rhythm
    'MusicRhythmPattern',

    # Generators
    'PatternGenerator',

    # Configuration
    'Config',
]
