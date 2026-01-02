"""Music Time Pattern Structures"""
from visualization import Cycle

class MusicTimeGrid:
    """Music Time Structure: meter and tempo"""
    # Horizontal time: rhythmic cycles and tempo
    def __init__(self,
            ticks_per_cycle: int = None,        # Number of ticks per cycle (measure, bar)
            # Meter structure
            beats_per_cycle: int = None,        # Number of beats in a cycle
            beat_start_ticks: list[int] = None, # Beat ticks
            # Rhythm patterns
            onset_start_ticks: list[int] = None, # Onset ticks for rhythm patterns
            # Notation
            beat_note: int = None, # Note value that gets the beat (e.g., 4 = quarter note)
            ):
        ### Relative timescale
        self.ticks_per_cycle = ticks_per_cycle # Tick is the smallest relative unit, represented as integer
        # Meter: measure cycle of beats
        self.beats_per_cycle = beats_per_cycle
        self.beat_start_ticks = beat_start_ticks
        # Rhythm: onset pattern
        self.onset_start_ticks = onset_start_ticks
        ### Notation: note value that gets the beat
        self.beat_note = beat_note

        self._cycle = Cycle(ticks_per_cycle, labels=[str(i+1) for i in range(ticks_per_cycle)])

    @classmethod
    def default_time(cls) -> "MusicTimeGrid":
        # Default relative time
        return MusicTimeGrid(
            ticks_per_cycle=16,
            beats_per_cycle=4,
            beat_note=4,
        )

    @property
    def ticks_per_beat(self):
        return self.ticks_per_cycle // self.beats_per_cycle

    def show(self):
        # Show time cycle
        self._cycle.show(title=f'Music Time Cycle: {self.ticks_per_cycle} ticks per cycle')

    def scale(self, scale_factor: float):
        """Scale the time signature and tempo of a MusicTimeGrid by a given factor."""
        self.ticks_per_cycle *= scale_factor
        self.beats_per_cycle = max(1, int(self.beats_per_cycle * scale_factor))
        self.beat_note = max(1, int(self.beat_note * scale_factor))


class MusicRhythmPattern:
    """Common rhythms as onset interval patterns represented as tuples of integers."""
    _dict = {
        'Tresillo':     ( 8, (0, 3, 6)),
        'Shiko':        (16, (0, 4, 6, 10, 12)),
        'Soukous':      (16, (0, 3, 6, 10, 11)),
        'Son Clave':    (16, (0, 3, 6, 10, 12)),
        'Rumba':        (16, (0, 3, 7, 10, 12)),
        'Bossa Nova':   (16, (0, 3, 6, 10, 13)),
        'Gahu':         (16, (0, 3, 6, 10, 14)),
        'Samba':        (16, (0, 3, 5, 7, 10, 12, 14)),
        'Fume-fume':    (12, (0, 2, 4, 7, 9)),
        'Bembe':        (12, (0, 2, 4, 5, 7, 9, 11)),
        'Steve Reich':  (12, (0, 1, 2, 4, 5, 7, 9, 10)),
        'One':          ( 8, (0,)),
        'Two':          ( 8, (0, 4)),
        'Three':        (12, (0, 4, 8)),
        'Four':         (16, (0, 4, 8, 12)),
        }



    def __init__(self, time_grid: MusicTimeGrid, name: str = 'Simple'):
        self.time_grid = time_grid
        self.name = name
        self.onset_intervals = self._dict.get(name)


