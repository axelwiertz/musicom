"""Music time representation: rhythm and meter as circular structures."""

from structures.circle import Circle

class MusicTime (Circle):
    # Rhythm and meter
    def __init__(self,
                 timesteps: int = 8, # Number of timesteps (ticks) per cycle
                 beats_in_measure: int = 4,
                 beat_note: int = 4,
                 bpm: int = 100):
        # Timestep is the smallest rhythm relative unit, represented as integer
        self.timesteps = timesteps
        super().__init__(timesteps, labels=[str(i+1) for i in range(timesteps)])
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        self.bpm = bpm
