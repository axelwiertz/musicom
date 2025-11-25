from typing import List
from structures.grid import Matrix

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
