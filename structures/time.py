"""Music Time Structure: meter and tempo"""
from .timegrid import MusicTimeGrid

class TempoRange:
    """Common tempo ranges in BPM for different music styles."""
    _dict = {
        'Ballad': (60, 80),
        'Pop': (100, 130),
        'Rock': (120, 160),
        'EDM / Dance': (120, 140),
        'Techno': (125, 150),
        'Drum & Bass': (160, 180),
        'Classical (Allegro)': (120, 168),
        'Classical (Adagio)': (66, 76)
    }
    @classmethod
    def get_range(cls, style: str):
        """Get tempo range for a given music style."""
        return cls._dict.get(style, (60, 120))  # Default to (60, 120) if style not found

    @classmethod
    def styles(cls):
        """Get a list of available music styles."""
        return list(cls._dict.keys())


class MusicLinearTime:
    """Music Linear Time Structure"""
    def __init__(self,
                time_grid: MusicTimeGrid = None,
                bpm: int = None  # beats per minute
                 ):
        ### Linear timescale
        self.time_grid = time_grid if time_grid else MusicTimeGrid.default_time()
        # Tempo
        self.bpm = bpm

    def seconds_per_cycle(self) -> float:
        return self.seconds_per_beat * self.time_grid.beats_per_cycle
    @property
    def seconds_per_beat(self) -> int:
        return 60.0 / self.bpm if self.bpm else 0
    @property
    def seconds_per_tick(self) -> float:
        return self.seconds_per_beat / self.time_grid.ticks_per_beat if self.time_grid.ticks_per_beat else 0

