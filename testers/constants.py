
def contants_test():
    tt = TwelveTET()
    print("12-TET Pitch Frequencies:")
    for i in range(12):
        freq = tt.midi_to_freq(i + MIDIpitch.C4)
        name = tt.midi_to_name(i + MIDIpitch.C4)
        print(f"{name} (MIDI {i + MIDIpitch.C4}) = {freq:.2f} Hz")
    print("Pitch frequencies:")
    for pitch in ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']:
        midi = tt.name_to_midi(pitch)
        freq = tt.midi_to_freq(midi)
        print(f"{pitch} (MIDI {midi}) = {freq:.2f} Hz")
    print("Test:")
    print("A4 ->", tt.midi_to_freq(69))
    print("C4 ->", tt.name_to_midi("C4"))
    print("C4 ->", tt.midi_to_freq(tt.name_to_midi("C4")))
    print("440 Hz -> MIDI", tt.freq_to_midi(440.0))
    print("Cents between 440 and 466.16:", tt.cents_between(440.0, 466.1637615180899))


if __name__ == "__main__":
    main()
