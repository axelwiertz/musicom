""" """
from typing import Optional, List
from structures.unit import MusicUnit
from structures.composition import MusicVoice

# The `Matrix` class is a 2D grid that holds `MusicUnit` objects.

class Matrix:
    """Represents a 2D matrix of MusicUnit objects."""
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Optional[MusicUnit]]] = [[None for _ in range(cols)] for _ in range(rows)]

    def set_unit(self, row: int, col: int, unit: MusicUnit):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = unit
        else:
            raise IndexError("Matrix index out of range.")

    def __repr__(self):
        return f"Matrix(rows={self.rows}, cols={self.cols})"


def test_grid():
    ### Usage Example
    # Here is how you can combine these classes to build a project structure.

    # 2. Create units with voices
    voice1 = MusicVoice(0, name="Melody")
    unit_a1 = MusicUnit(1)
    unit_a2 = MusicUnit(2)
    voice2 = MusicVoice(1, name="Bass")
    unit_b1 = MusicUnit(3)
    unit_b2 = MusicUnit(4)
    comp = MusicComposition(1, title="My First Song", voices=[voice1, voice2])

    # 3. Create a matrix and populate it with units
    main_matrix = Matrix(rows=2, cols=2)
    main_matrix.set_unit(0, 0, unit_a1)
    main_matrix.set_unit(0, 1, unit_a2)
    main_matrix.set_unit(1, 0, unit_b1)
    main_matrix.set_unit(1, 1, unit_b2)

    # 4. Create a section with the matrix
    intro_section = Section(name="Intro", matrix=main_matrix)

    # 5. Create a project and add the section
    my_project = Project(name="My First Song")
    my_project.add_section(intro_section)

    # Print the structure
    print(my_project)
    print(my_project.sections[0])
    print(my_project.sections[0].matrix.grid)
