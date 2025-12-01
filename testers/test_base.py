from base.twelvetone import TwelveTET
from base.midi import MidiPitch

def test_tuning():
    tet = TwelveTET.OCTAVES
    print(f"TwelveTET Octaves: {tet}")
    tet_pitch = TwelveTET.E
    print(tet_pitch)

def test_midi():
    midi_pitch = MidiPitch.C4  # Middle C
    print(f"MIDI Pitch: {midi_pitch}")

def test_pitch_intervals():
    from base.diatonic import get_pitch_intervals
    print("Pitch Intervals for Major Triad:", get_pitch_intervals(3, 3))
    print("Pitch Intervals for Minor7 Chord:", get_pitch_intervals(4, 1))
    print("Pitch Intervals for Dominant7 Chord:", get_pitch_intervals(4, 3))

def test_diatonic():
    from base.diatonic import DiatonicPatterns, Cardinality, PatternType

    pattern = DiatonicPatterns.dict[Cardinality.HEPTA][PatternType.SCALE]
    print("Diatonic Heptatonic Scale Pattern Intervals:", pattern)




def main():
    test_tuning()
    test_midi()
    test_pitch_intervals()
    test_diatonic()

if __name__ == "__main__":
    main()
