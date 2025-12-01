from base.midi import MidiPitch
from converters.pitch import midi_to_freq, name_to_midi, freq_to_midi, midi_to_name, cents_between

def test_pitch():
    print("12-TET Pitch Frequencies:")
    for i in range(12):
        freq = midi_to_freq(i + MidiPitch.C4)
        name = midi_to_name(i + MidiPitch.C4)
        print(f"{name} (MIDI {i + MidiPitch.C4}) = {freq:.2f} Hz")
    print("Pitch frequencies:")
    for pitch in ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']:
        midi = name_to_midi(pitch)
        freq = midi_to_freq(midi)
        print(f"{pitch} (MIDI {midi}) = {freq:.2f} Hz")
    print("Test:")
    print("A4 ->", midi_to_freq(69))
    print("C4 ->", name_to_midi("C4"))
    print("C4 ->", midi_to_freq(name_to_midi("C4")))
    print("440 Hz -> MIDI", freq_to_midi(440.0))
    print("Cents between 440 and 466.16:", cents_between(440.0, 466.1637615180899))

def main():
    test_pitch()

if __name__ == "__main__":
    main()