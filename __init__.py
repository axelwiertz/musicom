"""
Musicom - Music Composition Library
A Python library for algorithmic music composition, analysis, and generation.

Main modules:
- structures: Core music data structures (MusicUnit, MusicVoice, MusicSection, etc.)
- constants: Musical constants (TwelveTET, MIDI instruments)
- converters: Conversion between different music formats
- generators: Music generation algorithms
- rules: Music theory rules and harmony
- utilities: Helper utilities and configuration
"""

__version__ = '0.1.0'
__author__ = 'Musicom Team'

# Core structures
from .structures import (
    # Music structures
    MusicUnit,
    MusicVoice,
    MusicSection,
    MusicComposition,
    PercussionUnit,

    # Geometric structures
    Circle,
    Helix,

    # Music theory
    PitchRegister,
    Diatonic,
    MusicPattern,
    MusicScale,
    MusicalInterval,
    PatternSequence,
    PitchClassSet,

    # Rhythm
    MusicTime,
    QuantizedEvent,

    # Visualization
    show_plot,
    rhythm_circle,
)

# Constants
from .constants import (
    TwelveTET,
    MIDIinstrument,
)

# Converters
from .converters import (
    unit_to_chord,
)

# Generators
from .generators import (
    Generator,
    SimpleGenerator,
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
    'MusicComposition',
    'PercussionUnit',

    # Geometric structures
    'Circle',
    'Helix',

    # Music theory
    'PitchRegister',
    'Diatonic',
    'MusicPattern',
    'MusicScale',
    'MusicalInterval',
    'PatternSequence',
    'PitchClassSet',

    # Rhythm
    'MusicTime',
    'QuantizedEvent',

    # Visualization
    'show_plot',

    # Constants
    'TwelveTET',
    'MIDIinstrument',

    # Converters
    'unit_to_chord',


    # Generators
    'Generator',
    'SimpleGenerator',

    # Configuration
    'Config',
]

