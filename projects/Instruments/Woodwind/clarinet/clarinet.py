# -*- coding: utf-8 -*-
"""Clarinet — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 71
GM_NAME = "Clarinet"
# RenderPipeline stem label: GM_PROGRAMS[71] = "Clarinet" (no quirk)
STEM_LABEL = "Clarinet"

# MIDI ranges (sounding pitch, Bb clarinet)
RANGE_MIN = 52      # E3 (chalumeau low E)
RANGE_MAX = 96      # C7 (altissimo practical top)
SOLO_RANGE = (60, 84)   # C4-C6 solo repertoire focus
SWEET_SPOT = (65, 83)   # F4-B5 clarion register, most characteristic

# Register zones
ZONES = {
    "low": (52, 66),     # chalumeau E3-G#4, dark woody
    "mid": (67, 83),     # throat+clarion G4-B5, warm singing
    "high": (84, 96),    # altissimo C6-C7, piercing bright
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.0),
    "tenuto": (70, 0.9),
    "staccato": (64, 0.25),
    "accent": (92, 0.9),
    "flutter": (66, 1.0),    # flutter-tongue, airy buzz
    "glissando": (72, 1.0),  # smear (Rhapsody-style), rare
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # odd-harmonic rich — cylindrical bore
    "mod_freq_ratio": 1.0,      # single-reed driven oscillator
    "mod_depth": 2.0,
    "attack": 0.05,             # reed/breath onset, faster than flute
    "release": 0.10,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, hall — shorter than flute, keep articulation
EQ_BODY = (450, -2.0)   # peaking cut Hz, dB — clear nasal honk
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — reed sparkle
PAN = 0.0               # center for solo; -0.15..-0.25 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
