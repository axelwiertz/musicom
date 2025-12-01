from structures import MusicMatrix, MusicUnit

# Create contrasting materials
unit_a = MusicUnit(1, "Motif 1", [60, 62, 64])
unit_b = MusicUnit(2, "Motif 2", [67, 65, 64])

matrix = MusicMatrix(rows=2, cols=4)
matrix.set_unit(0, 0, unit_a)
matrix.set_unit(1, 0, unit_b)

# Cross-pollinate materials
matrix.swap_cells((0, 1), (1, 1))  # Exchange at column 2
matrix.repeat_column(1, 2)          # Stabilize the exchange
matrix.repeat_column(0, 3)          # Return to original
