""" Rhythm generators """
from generators.base import Generator
from structures.unit import MusicUnit

class RhythmGenerator(Generator):
    def __init__(self,
                 source_unit: 'MusicUnit',
                 onsets: int = 4,
                 timesteps: int = 4):
        super().__init__(source_unit)
        self.onsets = onsets
        self.timesteps = timesteps

    def generate(self) -> list['MusicUnit']:
        return [MusicUnit(onset_intervals=euclidian(self.onsets, self.timesteps))]

# Euclidian rhythm generator
def euclidian (onsets: int = 4,
                      timesteps: int = 4 ) -> list[int] :
    # Divide number of onsets evenly over number of timesteps, reduced if duplicate

    # Onsets gets an equal timestep interval
    base_timestep_interval = timesteps // onsets
    # And the remaining timesteps are a separate time step interval
    remaining_timesteps = timesteps % onsets

    rhythm = []
    for i in range(onsets):
        rhythm_timestep_interval = base_timestep_interval
        if i < remaining_timesteps:
            rhythm_timestep_interval += 1
        rhythm.append (rhythm_timestep_interval)

    # Reduce
    while rhythm[0] != rhythm[-1]:
        for group in rhythm:
            if group != rhythm[-1]:
                    group += rhythm.pop(-1)

    last_interval = timesteps - sum(rhythm)
    if last_interval > 0:
        rhythm.append(last_interval)

    return rhythm
