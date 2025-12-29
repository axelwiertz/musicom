from visualization import Cycle


class MusicRhythmPattern:
    """Common rhythms as onset interval patterns represented as tuples of integers."""
    _dict = {
        'Simple': (1,),
        'Two': (1, 1),
        'Three': (1, 1, 1),
        'Four': (1, 1, 1, 1),
        'Tresillo': (3, 3, 2),
        'Twelve Eighth Bell': (2, 2, 1, 2, 2, 2, 1),
        'Son Clave': (3, 3, 4, 2, 4)
        }
    @classmethod
    def get_pattern(cls, name: str):
        """Get onset interval pattern by name."""
        return cls._dict.get(name, (1,))  # Default to 'Simple' if name not found
    @classmethod
    def patterns(cls):
        """Get a list of available pattern names."""
        return list(cls._dict.keys())


class MusicTimePattern:
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
    def default_time(cls) -> "MusicTimePattern":
        # Default relative time
        return MusicTimePattern(
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
        """Scale the time signature and tempo of a MusicTimePattern by a given factor."""
        self.ticks_per_cycle *= scale_factor
        self.beats_per_cycle = max(1, int(self.beats_per_cycle * scale_factor))
        self.beat_note = max(1, int(self.beat_note * scale_factor))
