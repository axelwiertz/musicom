from structures import MusicTime
from music21 import meter, tempo

def time_to_meter (time: MusicTime) -> meter.TimeSignature:
    # m21 meter
    time_signature = meter.TimeSignature(str(time.beats_in_measure) + '/' + str(time.beat_note))
    return time_signature

def timestep_duration_to_quarter_length (time: MusicTime, timestep_duration) -> float:
    # convert duration in timesteps to quarter length
    quarter_length = (timestep_duration *
                      (4 / time.beat_note) *
                      (time.beats_in_measure / time.timesteps))
    return quarter_length

def time_to_tempo (time: MusicTime) -> tempo.MetronomeMark:
    # m21 temp
    metronome_mark = tempo.MetronomeMark(number=time.bpm)
    return metronome_mark
