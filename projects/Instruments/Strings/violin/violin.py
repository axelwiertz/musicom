# -*- coding: utf-8 -*-
"""Violin — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 40
GM_NAME = "Violin"

# MIDI ranges
RANGE_MIN = 55      # G3
RANGE_MAX = 103     # E7
SWEET_SPOT = (67, 96)   # G4-B5 melodic focus

# Register zones
ZONES = {
    "low": (55, 66),
    "mid": (67, 84),
    "high": (85, 103),
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),
    "staccato": (68, 0.25),
    "spiccato": (62, 0.125),
    "tremolo": (72, 0.06),
    "pizzicato": (58, 0.2),
    "accent": (92, 0.9),
}

# Synthesis engine recommendation
SYNTHESIS = "bowed"     # sound/synthesis/bowed.py BowedString
MODAL_PRESET = "string"

# Production defaults
REVERB_TAIL = 2.0       # seconds, hall
EQ_AIR = (4000, 3.0)    # highshelf Hz, dB
PAN = 0.0               # center for solo


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
