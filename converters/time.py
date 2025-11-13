from structures import MusicTime
from music21 import meter, tempo

def time_to_meter (time: MusicTime) -> meter.TimeSignature:
    # m21 meter
    timesignature = meter.TimeSignature(str(time.beats_in_measure) + '/' + str(time.beat_note))
    return timesignature

def time_to_tempo (time: MusicTime) -> tempo.MetronomeMark:
    # m21 temp
    metronomemark = tempo.MetronomeMark(number=time.bpm)

    return metronomemark
