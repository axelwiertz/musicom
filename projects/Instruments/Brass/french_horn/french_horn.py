# -*- coding: utf-8 -*-
"""French Horn — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 60
GM_NAME = "French Horn"
# RenderPipeline stem label: GM_PROGRAMS[60] = "French Horn" (singular;
# TimGM6mb.sf2 preset 60 = "French Horns" plural — cosmetic only)
STEM_LABEL = "French Horn"

# MIDI ranges (sounding pitch; horn is an F transposing instrument)
RANGE_MIN = 41      # F2 (low practical; pedal tones to B1)
RANGE_MAX = 84      # C6 (orchestral top)
SOLO_RANGE = (53, 77)   # F3-F5 solo repertoire focus
SWEET_SPOT = (55, 72)   # G3-C5 most characteristic, warm singing

# Register zones
ZONES = {
    "low": (41, 55),     # F2-G3 dark mellow, section blend
    "mid": (56, 72),     # G#3-C5 warm round, horn-section foundation
    "high": (73, 84),    # C#5-C6 bright heroic, thins above G5
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),
    "tenuto": (72, 0.9),
    "staccato": (64, 0.25),
    "marcato": (92, 0.9),
    "sforzando": (100, 0.7),
    "stopped": (60, 1.0),   # hand/mute — nasal buzzy
    "flutter": (75, 1.0),
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # rich harmonics — conical bore brass
    "mod_freq_ratio": 1.0,      # 1:1 FM, brass-like spectrum
    "mod_depth": 2.5,           # rounder than trumpet (4.0), fuller than trombone
    "attack": 0.07,             # horn blooms slowest of brass (40-80 ms)
    "release": 0.13,
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, hall — solo horn needs space
EQ_BODY = (450, -2.0)   # peaking cut Hz, dB — clear nasal honk
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — horn presence
PAN = 0.0               # center for solo; ±0.3 spread for section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
