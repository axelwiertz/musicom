"""Music time representation: rhythm and meter as circular structures."""
from visualization import Cycle

class MusicTime:
    # Horizontal time: rhythmic cycles and tempo
    def __init__(self,
                 timesteps: int = 8, # Number of timesteps (ticks) per cycle (measure, bar)
                 beats_in_measure: int = 4, # Number of beats in a measure
                 beat_note: int = 4, # Note value that gets the beat (e.g., 4 = quarter note)
                 bpm: int = 100, # Tempo in beats per minute
                 ):
        # Relative time: rhythmic cycles
        # Timestep (tick) is the smallest relative unit, represented as integer
        self.timesteps = timesteps
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        # Linear time: real time / play
        # tempo
        self.bpm = bpm
        self.seconds_per_beat = 60.0 / bpm

        self._cycle = Cycle(timesteps, labels=[str(i+1) for i in range(timesteps)])

    def show(self):
        # Show time cycle
        self._cycle.show(title=f'Music Time Cycle: {self.timesteps} timesteps per measure')