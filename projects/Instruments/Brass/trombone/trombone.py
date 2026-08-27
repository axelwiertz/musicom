# -*- coding: utf-8 -*-
"""Trombone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 57
GM_NAME = "Trombone"

# MIDI ranges
RANGE_MIN = 40      # E2
RANGE_MAX = 78      # F5
SOLO_RANGE = (52, 72)   # E3-C5 singing/lead focus
SWEET_SPOT = (55, 70)   # G3-A4 most characteristic

# Register zones
ZONES = {
    "low": (40, 53),
    "mid": (54, 65),
    "high": (66, 78),
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),
    "tenuto": (72, 0.9),
    "staccato": (64, 0.25),
    "marcato": (92, 0.9),
    "sforzando": (104, 0.7),
    "glissando": (70, 1.0),
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,      # odd/even partial mix — brass-like
    "mod_depth": 3.0,
    "attack": 0.04,             # lip/breath onset, slower than trumpet
    "release": 0.12,
}

# Production defaults
REVERB_TAIL = 1.2       # seconds, hall — less than trumpet
EQ_BODY = (350, -2.0)   # peaking cut Hz, dB — clear nasal honk
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — cut through mix
PAN = 0.0               # center for solo; -0.2..-0.3 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
