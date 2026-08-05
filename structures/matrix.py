from .unit import MusicUnit
from .time import TimeConverter
from typing import List, Optional, Tuple, Any, Callable, Sequence
import numpy as np


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

    def get_unit(self, pos: Tuple[int, int]) -> Optional[MusicUnit]:
        """Get the MusicUnit at the specified position."""
        row, col = pos
        return self.data[row, col]

    def set_unit(self, pos: Tuple[int, int], unit: Optional[MusicUnit]):
        """Set a MusicUnit at the specified position."""
        row, col = pos
        self.data[row, col] = unit

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
    def mutate_unit(self, pos: Tuple[int, int], func: Callable[[Any], Any]):
        row, col = pos
        self.data[row, col] = func(self.data[row, col])

    def swap_units(self, a: Tuple[int, int], b: Tuple[int, int]):
        ra, ca = a
        rb, cb = b
        self.data[ra, ca], self.data[rb, cb] = self.data[rb, cb], self.data[ra, ca]

    # UnitMatrix operations
    def transpose_matrix(self, copy_matrix: bool = False) -> "UnitMatrix":
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

    # ==================== TIME VALIDATION METHODS ====================

    def get_row_length(self, row: int) -> int:
        """Get total length of a row in ticks.
        
        Args:
            row: Row index (voice)
            
        Returns:
            Total ticks for all units in this row
        """
        units = self.units_in_row(row)
        return sum(unit.len_ticks() for unit in units)

    def get_all_row_lengths(self) -> List[int]:
        """Get total length of each row in ticks.
        
        Returns:
            List of tick lengths, one per row
        """
        lengths = []
        for r in range(self.num_rows):
            lengths.append(self.get_row_length(r))
        return lengths

    def validate_timing(self) -> bool:
        """Check all rows have the same total duration.
        
        This is CRITICAL for MIDI export - all tracks must align.
        
        Low-level structural check returning a bare boolean. For a user-facing
        validation that also returns an error message, use
        ``UnitMatrixComposer.validate()`` which returns ``(bool, str)``.
        
        Returns:
            True if all rows have identical total tick count, False otherwise
        """
        lengths = self.get_all_row_lengths()
        return len(set(lengths)) == 1

    def get_row_events(self, row: int) -> List:
        """Get all MusicEvents for a row, time-aligned across columns.
        
        Events from each unit in the row are offset by the cumulative
        length of previous units in that row.
        
        Args:
            row: Row index (voice)
            
        Returns:
            List of MusicEvent with absolute ticks
        """
        return TimeConverter.align_units_to_track(self.units_in_row(row))

    def get_all_track_events(self) -> List[List]:
        """Get all events for all rows as separate tracks.
        
        Returns:
            List of event lists, one per row (track)
        """
        tracks = []
        for r in range(self.num_rows):
            tracks.append(self.get_row_events(r))
        return tracks

    def get_track_length(self) -> int:
        """Get the common track length in ticks.
        
        Returns:
            Total ticks if all rows aligned, 0 otherwise
        """
        if self.validate_timing():
            return self.get_row_length(0)
        return 0

    # ==================== MIDI EXPORT METHODS ====================

    def to_midi_track_messages(self, row: int, program: int = 0, 
                               channel: int = 0) -> List:
        """Convert a row to MIDI messages with delta times.
        
        Args:
            row: Row index (voice)
            program: MIDI program number (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            List of mido.Message objects ready for MIDI track
        """
        events = self.get_row_events(row)
        delta_events = TimeConverter.events_to_delta(events)
        return TimeConverter.track_to_midi_messages(delta_events, program, channel)

    # ==================== ROW TRANSFORMATIONS ====================

    def transpose_row(self, row: int, interval_: int):
        """Transpose (shift) the pitches of a row of units by a given interval.
        Args:
            row (int): The row index to transpose.
            interval_ (int): The interval by which to transpose the pitches.
        """
        for c in range(self.data.shape[self.COL]):
            cell: Optional[MusicUnit] = self.data[row, c]
            if cell is not None:
                self.data[row, c] = cell.transpose(interval_)

    def retrograde_row(self, row: int):
        """Retrograde (reverse) the order of units in a given row.
        Args:
            row (int): The row index to retrograde.
        """
        cols = self.data.shape[self.COL]
        for c in range(cols // 2):
            cell_a = self.data[row, c]
            cell_b = self.data[row, cols - 1 - c]
            self.data[row, c], self.data[row, cols - 1 - c] = cell_b, cell_a

    def invert_row(self, row: int, pivot: Optional[int] = None):
        """Invert the pitches of units in a given row around a pivot point.
        Args:
            row (int): The row index to invert.
            pivot (Optional[int], optional): The pivot pitch. If None, uses the first pitch node's pitch of the first unit. Defaults to None.
        """
        for c in range(self.data.shape[self.COL]):
            cell: Optional[MusicUnit] = self.data[row, c]
            if cell is not None:
                self.data[row, c] = cell.invert(pivot)

    def augment_row(self, row: int, factor: float):
        """Augment (scale) the durations of units in a given row by a factor.
        Args:
            row (int): The row index to augment.
            factor (float): The factor by which to scale the durations.
        """
        for c in range(self.data.shape[self.COL]):
            cell: Optional[MusicUnit] = self.data[row, c]
            if cell is not None:
                self.data[row, c] = cell.augment(factor)