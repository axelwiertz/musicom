class Voice:
    """Represents a voice or layer in the project."""
    def __init__(self, voice_id: int, name: str):
        self.voice_id = voice_id
        self.name = name

    def __repr__(self):
        return f"Voice(id={self.voice_id}, name='{self.name}')"

from typing import Any, Optional

class Unit:
    """Represents a single unit of data, optionally associated with a voice."""
    def __init__(self, data: Any, voice: Optional[Voice] = None):
        self.data = data
        self.voice = voice

    def __repr__(self):
        return f"Unit(data={self.data}, voice={self.voice})"

# The `Matrix` class is a 2D grid that holds `Unit` objects.

from typing import List

class Matrix:
    """Represents a 2D matrix of Unit objects."""
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Optional[Unit]]] = [[None for _ in range(cols)] for _ in range(rows)]

    def set_unit(self, row: int, col: int, unit: Unit):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = unit
        else:
            raise IndexError("Matrix index out of range.")

    def __repr__(self):
        return f"Matrix(rows={self.rows}, cols={self.cols})"

#The `Section` class contains a `Matrix` and other section-specific metadata.

class Section:
    """Represents a project section, containing a matrix."""
    def __init__(self, name: str, matrix: Matrix):
        self.name = name
        self.matrix = matrix

    def __repr__(self):
        return f"Section(name='{self.name}', matrix={self.matrix})"

# Finally, the `Project` class is the top-level container for a list of `Section` objects.

class Project:
    """Represents the entire project, containing multiple sections."""
    def __init__(self, name: str):
        self.name = name
        self.sections: List[Section] = []

    def add_section(self, section: Section):
        self.sections.append(section)

    def __repr__(self):
        return f"Project(name='{self.name}', sections={len(self.sections)})"

### Usage Example

# Here is how you can combine these classes to build a project structure.

# 1. Define voices
voice1 = Voice(voice_id=1, name="Melody")
voice2 = Voice(voice_id=2, name="Bass")

# 2. Create units with different data and voices
unit_a1 = Unit(data="C4", voice=voice1)
unit_a2 = Unit(data="E4", voice=voice1)
unit_b1 = Unit(data="C2", voice=voice2)
unit_b2 = Unit(data="G2", voice=voice2)

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
