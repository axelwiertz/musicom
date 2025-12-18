"""Defines constants for MIDI instruments, channels, and percussion mapping."""

class MidiInstrument:
    # General MIDI instrument numbers (0-127)
    PIANO = 1
    CHURCH_ORGAN = 20
    ACOUSTIC_GUITAR = 25
    VIOLIN = 41
    STRING_ENSEMBLE = 49
    TRUMPET = 57
    FLUTE = 74
    SYNTH_PAD = 88
    BASS = 33

    PERCUSSION = 128  # Channel 10 is percussion

class MidiChannel:
    PERCUSSION = 10  # Channel 10 (index 9) is reserved for percussion in General MIDI
    PERCUSSION_INDEX = 9

class MidiPercussion:
    # MIDI percussion mapping (channel 10): 35-81 common drums
    # See https://www.midi.org/specifications-old/item/gm-level-1-s
    BASS_DRUM = 36
    ACOUSTIC_SNARE = 38
    CLOSED_HI_HAT = 42
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