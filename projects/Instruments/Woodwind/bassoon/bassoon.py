# -*- coding: utf-8 -*-
"""Bassoon — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 70
GM_NAME = "Bassoon"
# RenderPipeline stem label: GM_PROGRAMS[70] = "Bassoon" (matches, no quirk;
# SF2 preset 70 also "Bassoon")
STEM_LABEL = "Bassoon"

# MIDI ranges (sounding pitch, concert bassoon)
RANGE_MIN = 34      # Bb1 (bassoon lowest note)
RANGE_MAX = 88      # E6 (practical solo top; altissimo to ~C6=84 common)
SOLO_RANGE = (43, 74)   # G2-D5 solo repertoire focus
SWEET_SPOT = (48, 72)   # C3-C5 most characteristic, singing tenor register

# Register zones
ZONES = {
    "low": (34, 52),     # Bb1-E3 bass register, reedy dark, tuba-like weight
    "mid": (53, 72),     # F3-C5 tenor register, warm vocal, money zone
    "high": (73, 88),    # Db5-E6 alto register, expressive, reedy thin at top
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (76, 1.0),
    "tenuto": (68, 0.9),
    "staccato": (60, 0.25),
    "marcato": (88, 0.9),
    "accent": (90, 0.9),
    "flutter": (64, 1.0),    # flutter-tongue, rare agitation effect
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "triangle",  # double-reed: strong fundamental + odd/even mix
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 2.0,           # moderate brightness — darker than oboe
    "attack": 0.06,             # double-reed speaks slow-ish (40-80 ms)
    "release": 0.12,
}

# Production defaults
REVERB_TAIL = 1.7       # seconds, hall — woodwind wind column, medium tail
EQ_BODY = (300, -2.5)   # peaking cut Hz, dB — clear tuba-like mud/boxiness
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — reed definition/sparkle
EQ_AIR = (6000, 1.5)    # highshelf Hz, dB — key/reed noise air, subtle
PAN = 0.0               # center for solo; -0.15..-0.25 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
