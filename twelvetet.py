"""
12-TET and MIDI
"""
from numpy import array
from math import pow, log2

class TwelveTET:
    # 12-Tone Equal Temperament tuning system
    TWELVE = 12  # Number of pitch classes 0-11
    CENTS : float = 100  # Cents in semitone
    A4_FREQ = 440.0  # Frequency of A4
    C = 0
    C_SHARP = D_FLAT = 1
    D = 2
    D_SHARP = E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = G_FLAT = 6
    G = 7
    G_SHARP = A_FLAT = 8
    A = 9
    A_SHARP = B_FLAT = 10
    B = 11
    PITCH_CLASS_NUMBERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    OCTAVES = 9  # Number of octaves in the pitch set

    PITCH_CLASS_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    PITCH_CLASS_NAMES_FLATMAP = {'D': 'C#', 'E': 'D#', 'G': 'F#', 'A': 'G#', 'B': 'A#', 'C': 'B', 'F': 'E'}

    def __init__(self):
        # Create pitch to frequency mapping
        self.pitch_numbers = array([x + str(y) for y in range(self.OCTAVES) for x in self.PITCH_CLASS_NAMES_SHARP])

        self.pitch_freqs = dict(
                            zip(self.pitch_numbers,
                                [2 ** ((n + 1 - 49) / 12) * TwelveTET.A4_FREQ for n in range(len(self.pitch_numbers))]
                                )
                            )
        self.pitch_freqs[''] = 0.0  # stop
        self.pitch_freqs = tuple(2 ** ((n - MIDIpitch.A4) / self.TWELVE) * self.A4_FREQ
                                        for n in self.PITCH_CLASS_NUMBERS)


    def midi_to_freq(self, midi):
        """Return frequency (Hz) for given MIDI note number (integer or float)."""
        return self.A4_FREQ * pow(2.0, (midi - MIDIpitch.A4) / float(self.TWELVE))

    def freq_to_midi(self, freq):
        """Return MIDI note number (can be fractional) for a given frequency (Hz)."""
        return MIDIpitch.A4 + float(self.TWELVE) * log2(freq / self.A4_FREQ)

    def semitone_ratio(self, n=1):
        """Return frequency ratio for n semitones: 2^(n/12)."""
        return pow(2.0, n / float(self.TWELVE))

    def cents_between(self, f1, f2):
        """Return difference in cents from f1 to f2 (positive if f2 > f1)."""
        return float(self.TWELVE) * log2(f2 / f1)

    def interval_cents(self, semitones):
        """Return cents value for given semitone interval."""
        return semitones * self.CENTS

    def midi_to_name(self, midi):
        """Return note name (e.g., C4, A4) for integer MIDI. If non-integer, rounds to nearest."""
        m = int(round(midi))
        name = self.PITCH_CLASS_NAMES_SHARP[m % self.TWELVE]
        octave = (m // self.TWELVE) - 1
        return f"{name}{octave}"

    def name_to_midi(self, name):
        """Parse note name like 'C#4' or 'A4' to MIDI number. Accepts flats as 'Bb'."""
        s = name.strip()
        # handle optional accidental and octave
        base = s[0].upper()
        accidental = ''
        rest = s[1:]
        if rest and rest[0] in ('#', 'b'):
            accidental = rest[0]
            rest = rest[1:]
        octave = int(rest) if rest else 4
        idx = base
        if accidental == '#':
            idx += '#'
        elif accidental == 'b':
            # convert flat to equivalent sharp
            idx = self.PITCH_CLASS_NAMES_FLATMAP.get(base, base)
        semitone_index = self.PITCH_CLASS_NAMES_SHARP.index(idx)
        return (octave + 1) * self.TWELVE + semitone_index


class MIDIpitch:
    # MIDI pitch numbers for common notes
    C4 = 60  # Middle C
    D4 = 62
    E4 = 64
    F4 = 65
    G4 = 67
    A4 = 69  # A above middle C (440 Hz)
    B4 = 71
    C5 = 72

class MIDIinstrument:
    # General MIDI instrument numbers (0-127)
    PIANO = 1
    CHURCH_ORGAN = 20
    ACOUSTIC_GUITAR = 25
    VIOLIN = 41
    STRING_ENSEMBLE = 49
    TRUMPET = 57
    FLUTE = 74
    SYNTH_PAD = 88

class MIDIchannel:
    PERCUSSION = 10  # Channel 10 (index 9) is reserved for percussion in General MIDI
    PERCUSSION_INDEX = 9

class MIDIpercussion:
    # MIDI percussion mapping (channel 10): 35-81 common drums
    # See https://www.midi.org/specifications-old/item/gm-level-1-s
    BASS_DRUM = 36
    ACOUSTIC_SNARE = 38
    CLOSED_HIHAT = 42
    LOW_TOM = 45
    MID_TOM = 47
    HIGH_TOM = 50
    RIDE_CYMBAL = 51
    CRASH_CYMBAL = 49
    HAND_CLAP = 39
    CLAVES = 75
    MARACAS = 70
    COWBELL = 56
    VIBRASLAP = 58
    WOODBLOCK = 76

def main():
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
    print("C4 ->", tt.midi_to_freq(t.name_to_midi("C4")))
    print("440 Hz -> MIDI", tt.freq_to_midi(440.0))
    print("Cents between 440 and 466.16:", tt.cents_between(440.0, 466.1637615180899))


if __name__ == "__main__":
    main()
