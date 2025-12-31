import numpy as np

from structures import MusicProject, UnitMatrix, MusicUnit, MusicTimePattern
from converters.pitch import name_to_midi

# Create a music project with a unit matrix
proj = MusicProject(name="Systematic Composition",
                    time_pattern = MusicTimePattern(ticks_per_cycle=16, beats_per_cycle=4),
                    matrix = UnitMatrix(),
                    )

events = np.array([60, 80, 0, 6])

motif_a = MusicUnit(pitches=[60, 64]
    )
motif_b = MusicUnit(pitches=[name_to_midi('G4'), name_to_midi('B4'), 67]
    )

# Populate the matrix
proj.matrix.set_unit(0, 0, motif_a)
proj.matrix.set_unit(1, 0, motif_b)

# Apply compositional transformations

# Row operations (voice transformations)
proj.matrix.transpose_row(0, 2)  # Transpose voice 1 up by 2 semitones
proj.matrix.retrograde_row(1)  # Play voice 2 backward
proj.matrix.invert_row(2, pivot=60)  # Mirror melodic contours around middle C
proj.matrix.augment_row(3, factor=2.0)  # Double note durations in voice 4

# Column operations (sectional development)
proj.matrix.repeat_column(0, 3)  # Repeat section 1 at position 3
transition = [MusicUnit(pitches=[65, 67, 69])]*4  # Transitional material
proj.matrix.insert_column(2, transition)  # Insert transitional material
proj.matrix.reorder_columns([0, 2, 1, 3])  # Non-linear narrative structure

# Cell operations (unit manipulation)
proj.matrix.swap_units((0, 0), (1, 1))  # Exchange material between voices
proj.matrix.mutate_unit(0, 0, lambda unit: unit.transpose(5) if unit else None)

# Matrix operations
diagonal = proj.matrix.diagonal_read()  # Extract diagonal pattern
transposed = proj.matrix.transpose_matrix()  # Swap rows and columns (voices ↔ sections)
# Selectively erase units with low pitch
proj.matrix.selective_erase(lambda r, c, unit: unit is not None and min(unit.pitches) < 60)
