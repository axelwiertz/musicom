"""Music Time Structure"""

from visualization import Cycle

class MusicTime:
    """Music Time Structure: meter and tempo"""
    # Horizontal time: rhythmic cycles and tempo
    def __init__(self,
                # Rhythmic structure
                ticks_per_cycle: int = 8, # Number of ticks per cycle (measure, bar)
                beats_per_cycle: int = 4, # Number of beats in a cycle
                # Notation
                beat_note: int = 4, # Note value that gets the beat (e.g., 4 = quarter note)
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
        self.ticks_per_beat = ticks_per_cycle // beats_per_cycle
        self.seconds_per_beat = 60.0 / bpm
        self.seconds_per_cycle = self.seconds_per_beat * beats_per_cycle

        self._cycle = Cycle(ticks_per_cycle, labels=[str(i+1) for i in range(ticks_per_cycle)])

    def show(self):
        # Show time cycle
        self._cycle.show(title=f'Music Time Cycle: {self.ticks_per_cycle} ticks_per_cycle per measure')

    def scale(self, scale_factor: float):
        """Scale the time signature and tempo of a MusicTime by a given factor."""
        self.ticks_per_cycle *= scale_factor
        self.beats_per_cycle = max(1, int(self.beats_per_cycle * scale_factor))
        self.beat_note = max(1, int(self.beat_note * scale_factor))
