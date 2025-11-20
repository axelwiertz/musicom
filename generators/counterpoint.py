"""
Musicom generators module - counterpoint
"""
from structures import MusicUnit
from analysis.music21 import stream, interval


def stream_is_counterpoint(unit1: MusicUnit, unit2: MusicUnit) -> bool:
    # Check two counterpoint voices
    stream1 = unit1.stream
    stream2 = unit2.stream
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


def create_counterpoint(voice1: MusicUnit = None) -> MusicUnit:
    # Create a two-voice counterpoint composition
    voice2 = MusicUnit()
    voice2.stream = stream_create_random_from_list(length)

    # Keep generating until counterpoint reached
    while not stream_is_counterpoint(voice1, voice2):
        voice2 = stream_create_random_from_list(length)

    return voice2
