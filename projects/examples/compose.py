import numpy as np

from converters.pitch import name_to_midi
from structures import MusicProject, UnitMatrix, MusicUnit, MusicTimePattern

proj = MusicProject("Systematic Composition")
matrix = UnitMatrix()
time = MusicTimePattern(16, 4)

events = np.array([60, 80, 0, 6])

motif_a = MusicUnit("Motif a", pitches=[60, 64]
    )
motif_b = MusicUnit("Motif b", pitches=[name_to_midi('G4'), name_to_midi('B4'), 67]
    )

# Populate the matrix
matrix.set_cell(0, 0, motif_a)
matrix.set_cell(1, 0, motif_b)

# Apply compositional transformations

# Row operations (voice transformations)
matrix.transpose_row(0, 2)  # Transpose voice 1 up by 2 semitones
matrix.retrograde_row(1)  # Play voice 2 backward
matrix.invert_row(2, pivot=60)  # Mirror melodic contours around middle C
matrix.augment_row(3, factor=2.0)  # Double note durations in voice 4

# Column operations (sectional development)
matrix.repeat_column(0, 3)  # Repeat section 1 at position 3
transition = MusicUnit("Transition", pitches=[65, 67, 69])
matrix.insert_column(2, transition)  # Insert transitional material
matrix.reorder_columns([0, 2, 1, 3])  # Non-linear narrative structure

# Cell operations (unit manipulation)
matrix.swap_cells((0, 0), (1, 1))  # Exchange material between voices
matrix.mutate_cell(0, 0, lambda cell: cell.transpose(5) if cell else None)

# Matrix operations
diagonal = matrix.diagonal_read()  # Extract diagonal pattern
transposed = matrix.transpose()  # Swap rows and columns (voices ↔ sections)
matrix.selective_erase(
    condition=lambda cell: cell is None or cell.metadata.get("density", 0) < 0.5
)

