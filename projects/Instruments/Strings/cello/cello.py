# -*- coding: utf-8 -*-
"""Cello — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 42
GM_NAME = "Cello"

# MIDI ranges
RANGE_MIN = 36      # C2 (open lowest string)
RANGE_MAX = 84      # C6 (solo extension; orchestral tops out ~E5-A5 76-81)
SOLO_RANGE = (48, 76)   # C3-E5 solo repertoire focus
SWEET_SPOT = (48, 67)   # C3-G4 singing register, projects well

# Register zones
ZONES = {
    "low": (36, 47),
    "mid": (48, 67),
    "high": (68, 84),
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (78, 1.0),
    "staccato": (66, 0.25),
    "spiccato": (60, 0.125),
    "tremolo": (70, 0.06),
    "pizzicato": (56, 0.2),
    "accent": (90, 0.9),
}

# Synthesis engine recommendation
SYNTHESIS = "bowed"     # sound/synthesis/bowed.py BowedString
MODAL_PRESET = "string" # pizzicato via ModalSynth

# Production defaults
REVERB_TAIL = 2.5       # seconds, hall — larger body than violin
EQ_BODY = (300, -3.0)   # peaking cut Hz, dB — remove boxiness
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — bow noise/wood
PAN = 0.0               # center for solo; -0.2..-0.3 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
