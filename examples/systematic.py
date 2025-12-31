"""Example of systematic musical development using transformations"""

from structures import MusicProject, UnitMatrix, MusicUnit, MusicSection
from converters.music21_score import project_to_score
from converters.musicpy_converter import piece_play
from converters.music21_musicpy import score_to_piece

# Create a theme and develop it systematically
theme = MusicUnit(pitches=[60, 64, 67])
proj = MusicProject(name="Systematic Composition",
                    matrix=UnitMatrix(shape=(4, 8)),
                    sections=[MusicSection("Section A")])

# Voice 1: Original theme
proj.matrix.set_unit(0, 0, theme)

# Voice 2: Inverted theme
proj.matrix.set_unit(row=1, col=0, unit=theme)
proj.matrix.invert_row(row=1, pivot=64)

# Voice 3: Retrograde theme
proj.matrix.set_unit(row=2, col=0, unit=theme)
proj.matrix.retrograde_row(row=2)

# Voice 4: Augmented theme
proj.matrix.set_unit(row=3, col=0, unit=theme)
proj.matrix.augment_row(row=3, factor=2.0)

# Develop across sections
for col in range(1, 8):
    proj.matrix.repeat_column(0, col)
    # Apply variations to each section
    proj.matrix.get_unit(0, col).transpose(col % 12)

score = project_to_score(proj)
piece_play(score_to_piece(score))