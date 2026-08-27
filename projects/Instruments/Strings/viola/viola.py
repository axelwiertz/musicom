# -*- coding: utf-8 -*-
"""Viola — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 41
GM_NAME = "Viola"

# MIDI ranges
RANGE_MIN = 48      # C3 (open lowest string)
RANGE_MAX = 91      # G6 (solo extension; orchestral tops out ~E6 88)
SOLO_RANGE = (55, 79)   # G3-G5 solo repertoire focus
SWEET_SPOT = (60, 76)   # C4-E5 singing register, projects well

# Register zones
ZONES = {
    "low": (48, 59),
    "mid": (60, 71),
    "high": (72, 91),
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),
    "staccato": (66, 0.25),
    "spiccato": (60, 0.125),
    "tremolo": (70, 0.06),
    "pizzicato": (58, 0.2),
    "accent": (92, 0.9),
}

# Synthesis engine recommendation
SYNTHESIS = "bowed"     # sound/synthesis/bowed.py BowedString
MODAL_PRESET = "string" # pizzicato via ModalSynth

# Production defaults
REVERB_TAIL = 2.2       # seconds, hall — between violin (2.0) and cello (2.5)
EQ_BODY = (300, -2.5)   # peaking cut Hz, dB — remove boxiness/nasal
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — bow/wood presence
PAN = 0.0               # center for solo; -0.15..-0.25 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
