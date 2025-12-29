"""Converters between MusicTimePattern and music21 time and tempo representations."""
from structures.time import MusicTimePattern
from music21 import meter, tempo

def time_to_meter (time: MusicTimePattern) -> meter.TimeSignature:
    # m21 meter
    time_signature = meter.TimeSignature(str(time.beats_per_cycle) + '/' + str(time.beat_note))
    return time_signature

def meter_to_time (time_signature: meter.TimeSignature, ticks: int, bpm: int) -> MusicTimePattern:
    # convert m21 meter to MusicTimePattern
    time = MusicTimePattern(
        beats_per_cycle=time_signature.numerator,
        beat_note=time_signature.denominator,
        bpm=bpm,
        ticks_per_cycle=ticks
    )
    return time

def ticks_to_quarter_length (ticks : int,
                             time: MusicTimePattern,
                             ) -> float:
    # convert duration in ticks to quarter length
    quarter_length = (ticks *
                      (4 / time.beat_note) *
                      (time.beats_per_cycle / time.ticks_per_cycle))
    return quarter_length

def quarter_length_to_ticks (quarter_length: float,
                             time: MusicTimePattern,
                             ) -> int:
    # convert quarter length to duration in ticks
    ticks = int(quarter_length *
                (time.beat_note / 4) *
                (time.ticks_per_cycle / time.beats_per_cycle))
    return ticks

def time_to_tempo (time: MusicTimePattern) -> tempo.MetronomeMark:
    # m21 temp
    metronome_mark = tempo.MetronomeMark(number=time.bpm)
    return metronome_mark



