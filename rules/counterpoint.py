"""
Musicom generators module - counterpoint
"""
from structures import MusicUnit
from music21 import interval
from converters.m21 import unit_to_stream


def is_counterpoint(unit1: MusicUnit, unit2: MusicUnit) -> bool:
    # Check two counterpoint voices
    stream1 = unit_to_stream(unit1)
    stream2 = unit_to_stream(unit2)
    # Ensure the voices are of the same length
    if len(stream1) != len(stream2):
        raise ValueError("Voices must be of the same length")

    # Check for parallel perfect intervals
    for i in range(len(stream1) - 1):
        intv1 = interval.DiatonicInterval(stream1[i], stream1[i + 1])
        intv2 = interval.DiatonicInterval(stream2[i], stream2[i + 1])
        if intv1.perfectable and intv2.perfectable and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(stream1) - 1):
        intv1 = interval.DiatonicInterval(stream1[i], stream1[i + 1])
        intv2 = interval.DiatonicInterval(stream2[i], stream2[i + 1])
        if intv1.perfectable and intv2.perfectable and intv1.direction == intv2.direction:
            return False

    # Check for crossing voices
    for i in range(len(stream1) - 1):
        if stream1[i].pitch < stream2[i].pitch and stream1[i + 1].pitch > stream2[i + 1].pitch:
            return False

    return True
