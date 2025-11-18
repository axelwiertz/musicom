"""
Musicom converters package
Converters between different music representations (Music21, MusicPy, MusicUnit, etc.)
"""

from .time import time_to_meter, time_to_tempo
from .musiccomposition import voices_to_parts, parts_to_voices, score_set_time
from .musicunit import unit_to_excel, unit_to_dataframe

from .music21 import unit_to_stream, stream_to_unit, stream_to_chord, score_to_midifile, midifile_to_score
from .musicpy import track_to_print, unit_to_chord, chord_to_unit, chord_to_stream


__all__ = [
    # Print utilities
    'track_to_print',
    # Time converters
    'time_to_meter',
    'time_to_tempo',

    # Music21 converters
    'unit_to_stream',
    'stream_to_unit',
    'score_to_midifile',
    'midifile_to_score',

    # MusicPy converters
    'unit_to_chord',
    'chord_to_unit',
    'chord_to_stream',

    # MusicUnit converters
    'unit_to_excel',
    'unit_to_dataframe',

    # Stream/Chord converters
    'stream_to_chord',
    'chord_to_stream',

    # Composition converters
    'voices_to_parts',
    'parts_to_voices',
    'score_set_time',
]


