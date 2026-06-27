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

# Defer heavy imports to avoid circular/broken dependency issues at package level.
# Subpackages remain importable directly:
#   from musicom.ai.core.structures import Note, Phrase
#   from musicom.ai.rules.theories import HarmonyRules
