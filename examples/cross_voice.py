from structures import MusicProject, UnitMatrix, MusicUnit
from converters.musicpy_converter import project_to_piece

# Create contrasting materials
unit_a = MusicUnit(pitches=[60, 62, 64])
unit_b = MusicUnit(pitches=[67, 65, 64])

matrix = UnitMatrix(shape=(2,4))
matrix.set_unit(0, 0, unit_a)
matrix.set_unit(1, 0, unit_b)

# Cross-pollinate materials
matrix.swap_units((0, 1), (1, 1))  # Exchange at column 2
matrix.repeat_column(1, 2)          # Stabilize the exchange
matrix.repeat_column(0, 3)          # Return to original

proj = MusicProject(matrix=matrix)

piece = project_to_piece(proj)