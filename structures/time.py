"""Music Time Structure: meter and tempo"""
from visualization import Cycle

class MusicTime:
    """Music Time Structure: meter and tempo"""
    # Horizontal time: rhythmic cycles and tempo
    def __init__(self,
            # Rhythmic structure
            ticks_per_cycle: int = None, # Number of ticks per cycle (measure, bar)
            beats_per_cycle: int = None, # Number of beats in a cycle
            # Notation
            beat_note: int = None, # Note value that gets the beat (e.g., 4 = quarter note)
            # Tempo
            bpm: int = None, # beats per minute
            # Beat ticks
            beat_start_ticks: list[int] = None,
        ):
        # Relative timescale
        # Tick is the smallest relative unit, represented as integer
        self.ticks_per_cycle = ticks_per_cycle
        # Meter: measure cycle of beats
        self.beat_start_ticks = beat_start_ticks
        self.beats_per_cycle = beats_per_cycle
        # Notation: note value that gets the beat
        self.beat_note = beat_note
        # Linear time: real time / play
        # tempo
        self.bpm = bpm

        self._cycle = Cycle(ticks_per_cycle, labels=[str(i+1) for i in range(ticks_per_cycle)])

    @property
    def ticks_per_beat(self):
        return self.ticks_per_cycle // self.beats_per_cycle
    def seconds_per_cycle(self) -> float:
        return self.seconds_per_beat * self.beats_per_cycle
    @property
    def seconds_per_beat(self) -> int:
        return 60.0 / self.bpm if self.bpm else 0
    @property
    def seconds_per_tick(self) -> float:
        return self.seconds_per_beat / self.ticks_per_beat if self.ticks_per_beat else 0


    def show(self):
        # Show time cycle
        self._cycle.show(title=f'Music Time Cycle: {self.ticks_per_cycle} ticks per cycle')

    def scale(self, scale_factor: float):
        """Scale the time signature and tempo of a MusicTime by a given factor."""
        self.ticks_per_cycle *= scale_factor
        self.beats_per_cycle = max(1, int(self.beats_per_cycle * scale_factor))
        self.beat_note = max(1, int(self.beat_note * scale_factor))

    @classmethod
    def default_time(cls) -> "MusicTime":
        # Default time signature and tempo
        return MusicTime(
            ticks_per_cycle=16,
            beats_per_cycle=4,
            beat_note=4,
            bpm=120
        )