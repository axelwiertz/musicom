"""Example of systematic musical development using transformations"""

from structures import MusicMatrix,MusicUnit,MusicSection
from converters.music21_score import section_to_score
from converters.musicpy_converter import piece_play
from converters.music21_musicpy import score_to_piece
from transformers import PitchSequenceTransformer, retrograde, transpose, invert

# Create a theme and develop it systematically
theme = MusicUnit("Theme", [60, 64, 67])
section_a = MusicSection("Section A", None, MusicMatrix(rows=4, cols=8))

# Voice 1: Original theme
section_a.matrix.set_unit(0, 0, theme)

trans = PitchSequenceTransformer(theme)

# Voice 2: Inverted theme
section_a.matrix.set_unit(1, 0, theme)
for u in section_a.matrix.units_in_row (1):
    invert(u, 1, pivot=64)

# Voice 3: Retrograde theme
section_a.matrix.set_unit(2, 0, theme)
for u in section_a.matrix.units_in_row (2):
    retrograde(u)

# Voice 4: Augmented theme
section_a.matrix.set_unit(3, 0, theme)
for u in section_a.matrix.units_in_row (3):
    trans.set_unit(u)
    trans.change_durations(2.0)

# Develop across sections
for col in range(1, 8):
    section_a.matrix.repeat_column(0, col)
    # Apply variations to each section
    transpose(section_a.matrix.get_unit(0, col), col % 12)

score = section_to_score(section_a)
piece_play(score_to_piece(score))