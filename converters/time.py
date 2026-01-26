"""Converters between MusicTimeGrid and music21 time and tempo representations."""
from structures.time import MusicTimeGrid

def ticks_to_quarter_length(ticks, time_grid):
    """Convert ticks to quarter note length."""
    # calculate quarter length from ticks
    ticks_per_beat = time_grid.ticks_per_cycle / time_grid.beats_per_cycle
    quarter_length = ticks / ticks_per_beat
    return quarter_length

""" Deprecated functions below - use the above instead  
def ticks_to_quarter_length (ticks : int,
                             time: MusicTimeGrid,
                             ) -> float:
    # convert duration in ticks to quarter length
    quarter_length = (ticks *
                      (4 / time.beat_note) *
                      (time.beats_per_cycle / time.ticks_per_cycle))
    return quarter_length
"""

def quarter_length_to_ticks (quarter_length: float,
                             time: MusicTimeGrid,
                             ) -> int:
    # convert quarter length to duration in ticks
    ticks = int(quarter_length *
                (time.beat_note / 4) *
                (time.ticks_per_cycle / time.beats_per_cycle))
    return ticks