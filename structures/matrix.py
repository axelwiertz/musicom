"""MusicMatrix: A 2D matrix structure for musical material manipulation that holds `MusicUnit` objects"""

import numpy as np
from copy import deepcopy
from typing import Any, Callable, List, Optional, Sequence, Tuple
from structures.unit import MusicUnit


class MusicMatrix:
    """
    Basic 2D matrix for musical material:
    - horizontal rows are voices in pitch space
    - vertical columns are sections in time space
    Cells contain MusicUnit objects
    """
    def __init__(self,
                 rows: int = 0,
                 cols: int = 0,
                 data: Optional[List[List[MusicUnit]]] = None):

        if data is not None:
            # accept list-of-lists; normalize to list of lists
            self._data = [list(row) for row in data]
            if len(self._data) == 0:
                self._rows = self._cols = 0
            else:
                self._rows = len(self._data)
                self._cols = len(self._data[0])
                for r in self._data:
                    if len(r) != self._cols:
                        raise ValueError("All rows must have the same number of columns")
        else:
            self._rows = rows
            self._cols = cols
            self._data = [[None for _ in range(cols)] for _ in range(rows)]

        self.matrix = np.array(self._data)

    def __repr__(self):
        return f"Matrix(rows={self.rows}, cols={self.cols})"

    # Basic properties
    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    # Indexing: m[r] -> row list; m[r, c] -> element
    def __getitem__(self, key):
        if isinstance(key, tuple):
            r, c = key
            return self._data[r][c]
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            r, c = key
            self._data[r][c] = value
        else:
            self._data[key] = list(value)

    def clone(self) -> "MusicMatrix":
        return deepcopy(self)

    def __str__(self) -> str:
        # simple pretty print showing repr(cell) trimmed
        def fmt(x):
            s = repr(x)
            return s if len(s) <= 12 else s[:9] + "..."
        rows = ["\t".join(fmt(c) for c in row) for row in self._data]
        return "\n".join(rows)

    # Row operations
    def apply_to_row(self, r: int, func: Callable[[Any], Any], in_place: bool = True) -> Optional["MusicMatrix"]:
        if not (0 <= r < self._rows):
            raise IndexError("row index out of range")
        if in_place:
            self._data[r] = [func(c) for c in self._data[r]]
            return None
        new = self.clone()
        new._data[r] = [func(c) for c in new._data[r]]
        return new

    # Column operations
    def _get_column(self, c: int) -> List[Any]:
        if not (0 <= c < self._cols):
            raise IndexError("column index out of range")
        return [self._data[r][c] for r in range(self._rows)]

    def _set_column(self, c: int, col: Sequence[Any]):
        if len(col) != self._rows:
            raise ValueError("column length mismatch")
        for r in range(self._rows):
            self._data[r][c] = col[r]

    def apply_to_column(self, c: int, func: Callable[[Any], Any], in_place: bool = True) -> Optional["MusicMatrix"]:
        col = self._get_column(c)
        new_col = [func(x) for x in col]
        if in_place:
            self._set_column(c, new_col)
            return None
        new = self.clone()
        new._set_column(c, new_col)
        return new

    def repeat_column(self, c: int, times: int = 1, after: bool = True):
        if times < 1:
            return
        # build new columns list
        cols = [self._get_column(ci) for ci in range(self._cols)]
        insert_pos = c + 1 if after else c
        for _ in range(times):
            cols.insert(insert_pos, list(cols[c]))  # duplicate
            insert_pos += 1
        # rebuild data
        new_data = [[cols[col_idx][row_idx] for col_idx in range(len(cols))] for row_idx in range(self._rows)]
        self._data = new_data
        self._cols = len(cols)

    def insert_column(self, index: int, column_data: Sequence[Any]):
        if len(column_data) != self._rows:
            raise ValueError("column_data length must equal number of rows")
        cols = [self._get_column(ci) for ci in range(self._cols)]
        cols.insert(index, list(column_data))
        new_data = [[cols[col_idx][row_idx] for col_idx in range(len(cols))] for row_idx in range(self._rows)]
        self._data = new_data
        self._cols = len(cols)

    def reorder_columns(self, new_order: Sequence[int]):
        if len(new_order) != self._cols:
            raise ValueError("new_order must include each column index")
        cols = [self._get_column(ci) for ci in new_order]
        new_data = [[cols[col_idx][row_idx] for col_idx in range(len(cols))] for row_idx in range(self._rows)]
        self._data = new_data

    # Cell operations
    def mutate_cell(self, r: int, c: int, func: Callable[[Any], Any]):
        self._data[r][c] = func(self._data[r][c])

    def swap_cells(self, a: Tuple[int, int], b: Tuple[int, int]):
        ra, ca = a
        rb, cb = b
        self._data[ra][ca], self._data[rb][cb] = self._data[rb][cb], self._data[ra][ca]

    # MusicMatrix operations
    def transpose(self, copy_matrix: bool = False) -> "MusicMatrix":
        transposed = list(zip(*self._data))
        transposed = [list(row) for row in transposed]
        m = MusicMatrix(data=transposed)
        if copy_matrix:
            return m
        # in-place replace
        self._data = m._data
        self._rows, self._cols = m._rows, m._cols
        return self

    # alias rotate -> transpose (voices <-> sections)
    def rotate(self, copy_matrix: bool = False) -> "MusicMatrix":
        return self.transpose(copy_matrix=copy_matrix)

    def diagonal_read(self, start_col: int = 0) -> List[Any]:
        res = []
        r = 0
        c = start_col
        while r < self._rows and c < self._cols:
            res.append(self._data[r][c])
            r += 1
            c += 1
        return res

    def selective_erase(self, predicate: Callable[[int, int, Any], bool]):
        """
        Set cells to None where predicate(r, c, cell) is True.
        """
        for r in range(self._rows):
            for c in range(self._cols):
                if predicate(r, c, self._data[r][c]):
                    self._data[r][c] = None

    # Helper method to create a matrix from MusicUnit objects
    @classmethod
    def from_units(cls, units: List[List[MusicUnit]]) -> "MusicMatrix":
        """
        Create a MusicMatrix from a 2D list of MusicUnit objects.
        Args:
            units: 2D list horizontal rows and vertical columns of MusicUnit objects.
        Returns:
            MusicMatrix with the given units
        """
        return cls(data=units)

    def get_unit(self, row: int, col: int) -> Optional[MusicUnit]:
        """Get the MusicUnit at the specified position."""
        return self._data[row][col]

    def set_unit(self, row: int, col: int, unit: MusicUnit):
        """Set a MusicUnit at the specified position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._data[row][col] = unit
        else:
            raise IndexError("Matrix index out of range.")
