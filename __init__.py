"""
Musicom - Music Composition Library
A Python library for algorithmic music composition, analysis, and generation.

Flat package layout — each top-level directory is an importable package:

- structures: Core music data structures (MusicUnit, MusicEvent, UnitMatrix, ...)
- workflows: Composition workflows (UnitMatrixComposer, paradigm compare, provenance)
- generators: Algorithmic music generators
- rules: Music theory rules (counterpoint, progression, set theory, voice leading)
- transformers: Musical transformations
- converters: Format converters (MIDI, MusicXML, music21, musicpy)
- sound: Synthesis, effects, analysis, rendering, and sync
- visualization: Visual representations (grid, helix, cycle)
- analysis: Music analysis tools
- utilities: Helper utilities and configuration
"""

__version__ = '0.1.0'
__author__ = 'Musicom Team'

# Subpackages are imported directly, e.g.:
#   from structures import MusicUnit, MusicEvent, UnitMatrix
#   from workflows.unitmatrix_composer import UnitMatrixComposer
