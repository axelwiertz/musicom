"""Example of systematic musical development using transformations"""

from structures import MusicMatrix,MusicUnit
from converters import score_to_piece,piece_to_sound
from transformers import PitchSequenceTransformer, retrograde, transpose, invert

# Create a theme and develop it systematically
theme = MusicUnit(0, "Theme", [60, 64, 67])
matrix = MusicMatrix(rows=4, cols=8)

# Voice 1: Original theme
matrix.set_unit(0, 0, theme)

trans = PitchSequenceTransformer(theme)

# Voice 2: Inverted theme
matrix.set_unit(1, 0, theme)
for u in matrix.units_in_row (1):
    invert(u, 1, pivot=64)

# Voice 3: Retrograde theme
matrix.set_unit(2, 0, theme)
for u in matrix.units_in_row (2):
    retrograde(u)

# Voice 4: Augmented theme
matrix.set_unit(3, 0, theme)
for u in matrix.units_in_row (3):
    trans.set_unit(u)
    trans.change_durations(2.0)

# Develop across sections
for col in range(1, 8):
    matrix.repeat_column(0, col)
    # Apply variations to each section
    transpose(matrix.get_unit(0, col), col % 12)


score = matrix_to_score(matrix)
piece_play(score_to_piece(score))