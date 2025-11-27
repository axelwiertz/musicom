"""
Musicom - Music Composition Library
A Python library for algorithmic music composition, analysis, and generation.

Main modules:
- structures: Core music data structures (MusicUnit, MusicVoice, MusicSection, etc.)
- constants: Musical constants (TwelveTET, MIDI instruments)
- converters: Conversion between different music formats
- generators: Music generation algorithms
- regularity: Music theory regularity and harmony
- utilities: Helper utilities and configuration
"""

__version__ = '0.1.0'
__author__ = 'Musicom Team'

# Constants
from .constants import (
    TwelveTET,
    MidiInstrument,
)

# Core structures
from .structures import (
    # Music structures
    MusicUnit,
    MusicVoice,
    MusicSection,
    MusicComposition,

    # Music theory
    MusicPattern,
    MusicalInterval,
    PatternSequence,

    # Rhythm
    MusicTime,
    QuantizedEvent,
)
from .regularity import (
    PitchClassSet,
    Diatonic)

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
