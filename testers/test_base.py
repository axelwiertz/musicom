from base import Constants, PitchClass

def test_tuning():
    tet = Constants.OCTAVES
    print(f"TwelveTET Octaves: {tet}")
    tet_pitch = PitchClass.E
    print(tet_pitch)


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
    test_pitch_intervals()
    test_diatonic()

if __name__ == "__main__":
    main()
