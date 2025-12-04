"""
Musicom converters package
Converters between different music representations (Music21, MusicPy, MusicUnit, etc.)
"""

from .time import time_to_meter, time_to_tempo
from .project import score_to_section, section_to_score, score_to_piece, piece_to_score
from .unit import unit_to_excel, unit_to_dataframe
from .m21 import unit_to_stream, time_to_stream, stream_to_unit, score_to_midifile, midifile_to_score, stream_to_chord, pattern_to_m21scale, tonerow_to_stream
from .mp import track_to_print, unit_to_chord, chord_to_unit, chord_to_stream, piece_play, pattern_to_mpscale, midifile_to_piece
from .pitch import name_to_midi, midi_to_name


__all__ = [
    # Print utilities
    'track_to_print',
    # Time converters
    'time_to_meter',
    'time_to_tempo',

    # Music21 converters
    'unit_to_stream',
    'time_to_stream',
    'stream_to_unit',
    'score_to_midifile',
    'midifile_to_score',
    'pattern_to_m21scale',
    'tonerow_to_stream',

    # MusicPy converters
    'unit_to_chord',
    'chord_to_unit',
    'chord_to_stream',
    'piece_play',
    'pattern_to_mpscale',
    'midifile_to_piece',

    # Pitch converters
    'name_to_midi',
    'midi_to_name',

    # MusicUnit converters
    'unit_to_excel',
    'unit_to_dataframe',

    # Stream/Chord converters
    'stream_to_chord',
    'chord_to_stream',

    # Project converters
    'score_to_section',
    'section_to_score',
    'score_to_piece',
    'piece_to_score',

]


