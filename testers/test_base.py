from base.tuning import TwelveTET
from base.midi import MidiPitch



def test_pitch_intervals():
    from base.diatonic import get_pitch_intervals
    print("Pitch Intervals for Major Triad:", get_pitch_intervals(3, 3))
    print("Pitch Intervals for Minor7 Chord:", get_pitch_intervals(4, 1))
    print("Pitch Intervals for Dominant7 Chord:", get_pitch_intervals(4, 3))

def main():
    test_pitch_intervals()

if __name__ == "__main__":
    main()
