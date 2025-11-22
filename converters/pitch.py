"""Pitch and frequency conversion utilities."""

from math import pow, log2
from librosa import midi_to_hz, hz_to_midi, note_to_midi, midi_to_note
from constants.tuning import TwelveTET

def midi_to_freq(midi):
    """Return frequency (Hz) for given MIDI note number (integer or float).
    return self.A4_FREQ * pow(2.0, (midi - MIDIpitch.A4) / float(self.TWELVE))"""
    return midi_to_hz(midi)


def freq_to_midi(freq):
    """Return MIDI note number (can be fractional) for a given frequency (Hz).
    return MIDIpitch.A4 + float(self.TWELVE) * log2(freq / self.A4_FREQ)"""
    return hz_to_midi(freq)


def semitone_ratio(n=1):
    """Return frequency ratio for n semitones: 2^(n/12)."""
    return pow(2.0, n / float(TwelveTET.TWELVE))


def cents_between(f1, f2):
    """Return difference in cents from f1 to f2 (positive if f2 > f1)."""
    return float(TwelveTET.TWELVE) * log2(f2 / f1)


def interval_cents(semitones):
    """Return cents value for given semitone interval."""
    return semitones * TwelveTET.CENTS


def midi_to_name(midi):
    """Return note name (e.g., C4, A4) for integer MIDI. If non-integer, rounds to nearest.
    m = int(round(midi))
    name = self.PITCH_CLASS_NAMES_SHARP[m % self.TWELVE]
    octave = (m // self.TWELVE) - 1
    return f"{name}{octave}"""
    return midi_to_note(midi)


def name_to_midi(name):
    """Parse note name like 'C#4' or 'A4' to MIDI number. Accepts flats as 'Bb'.
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
    return (octave + 1) * self.TWELVE + semitone_index"""
    return note_to_midi(name)
