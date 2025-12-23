"""UnitMatrix: A 2D matrix structure for musical material manipulation that holds `MusicUnit` objects"""
import numpy as np
from typing import Any, Callable, List, Optional, Sequence, Tuple
from structures.unit import MusicUnit


class UnitMatrix:
    """
    Basic 2D matrix for MusicUnit objects:
    - horizontal rows are voices in pitch space
    - vertical columns are sections in time space
    """
    ROW = 0
    COL = 1
    def __init__(self, data = None, shape: Tuple[int, int] = None):
        if data is None and shape is None:
            raise ValueError("Either data or shape must be provided")
        self.data: np.ndarray
        if shape is not None:
            self.data = np.empty(shape, dtype=object)
        if data is not None:
            self.data = np.asarray(data)

    def __add__(self, other):
        return UnitMatrix(self.data + np.asarray(other))

    def __repr__(self):
        return f"UnitMatrix({self.data})"

    @property
    def num_rows(self) -> int:
        return self.data.shape[self.ROW]
    @property
    def num_cols(self) -> int:
        return self.data.shape[self.COL]

    def clone(self) -> "UnitMatrix":
        return UnitMatrix(data=self.data.copy())

    # Row operations
    def apply_to_row(self, r: int, func: Callable[[Any], Any]):
        self.data[r, :] = [func(unit) for unit in self.data[r, :]]

    def apply_to_column(self, c: int, func: Callable[[Any], Any],):
        self.data[:, c] = [func(x) for x in self.data[:, c]]

    def repeat_column(self, c: int, times: int = 1, after: bool = True):
        cols = self.data.shape[self.COL]
        if not (0 <= c < cols):
            raise IndexError("column index out of range")
        col_data = self.data[:, c:c+1]
        if after:
            self.data = np.insert(self.data, c + 1, np.tile(col_data, (1, times)), axis=1)
        else:
            self.data = np.insert(self.data, c, np.tile(col_data, (1, times)), axis=1)

    def insert_column(self, index: int, column_data: Sequence[Any]):
        rows, cols = self.data.shape
        if len(column_data) != rows:
            raise ValueError("column_data length must match number of rows")
        self.data = np.insert(self.data, index, column_data, axis=1)

    def reorder_columns(self, new_order: Sequence[int]):
        rows, cols = self.data.shape
        if len(new_order) != cols:
            raise ValueError("new_order must include each column index")
        if sorted(new_order) != list(range(cols)):
            raise ValueError("new_order must be a permutation of column indices")
        self.data = self.data[:, new_order]

    def units_in_row(self, r: int) -> List[MusicUnit]:
        rows, cols = self.data.shape
        if not (0 <= r < rows):
            raise IndexError("row index out of range")
        units: List[MusicUnit] = []
        for c in range(cols):
            unit = self.data[r, c]
            if unit is not None:
                units.append(unit)
        return units

    def units_in_col(self, c: int) -> List[MusicUnit]:
        rows, cols = self.data.shape
        if not (0 <= c < cols):
            raise IndexError("column index out of range")
        units: List[MusicUnit] = []
        for r in range(rows):
            unit = self.data[r, c]
            if unit is not None:
                units.append(unit)
        return units


    def reorder_rows(self, new_order: Sequence[int]):
        rows, cols = self.data.shape
        if len(new_order) != rows:
            raise ValueError("new_order must include each row index")
        if sorted(new_order) != list(range(rows)):
            raise ValueError("new_order must be a permutation of row indices")
        self.data = self.data[new_order, :]

    # Cell operations
    def mutate_cell(self, r: int, c: int, func: Callable[[Any], Any]):
        self.data[r, c] = func(self.data[r, c])

    def swap_cells(self, a: Tuple[int, int], b: Tuple[int, int]):
        ra, ca = a
        rb, cb = b
        self.data[ra, ca], self.data[rb, cb] = self.data[rb, cb], self.data[ra, ca]

    # UnitMatrix operations
    def transpose(self, copy_matrix: bool = False) -> "UnitMatrix":
        if copy_matrix:
            new = self.clone()
            new.data = new.data.T
            return new
        else:
            self.data = self.data.T
            return self

    def diagonal_read(self, start_col: int = 0) -> List[Any]:
        res: List[Any] = []
        r = 0
        c = start_col
        rows, cols = self.data.shape
        while r < rows and c < cols:
            res.append(self.data[r, c])
            r += 1
            c += 1
        return res

    def selective_erase(self, predicate: Callable[[int, int, Any], bool]):
        """
        Set cells to None where predicate(r, c, cell) is True.
        """
        rows, cols = self.data.shape
        for r in range(rows):
            for c in range(cols):
                if predicate(r, c, self.data[r, c]):
                    self.data[r, c] = None

    def get_unit(self, row: int, col: int) -> Optional[MusicUnit]:
        """Get the MusicUnit at the specified position."""
        return self.data[row, col]

    def set_unit(self, row: int, col: int, unit: Optional[MusicUnit]):
        """Set a MusicUnit at the specified position."""
        self.data[row, col] = unit
