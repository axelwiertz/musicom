# -*- coding: utf-8 -*-
"""Tuba — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 58
GM_NAME = "Tuba"
# RenderPipeline stem label: GM_PROGRAMS[58] = "Tuba" (matches, no quirk;
# SF2 preset 58 also "Tuba")
STEM_LABEL = "Tuba"

# MIDI ranges (sounding pitch; CC/BBb tuba)
RANGE_MIN = 26      # D1 (orchestral low; pedal C1=24 possible on CC)
RANGE_MAX = 72      # C5 (virtuoso top; orchestral tops ~F4=65)
SOLO_RANGE = (36, 62)   # C2-D4 solo repertoire focus
SWEET_SPOT = (43, 58)   # G2-Bb3 most characteristic, foundation register

# Register zones
ZONES = {
    "low": (26, 42),     # D1-F2 pedal/contra, dark sub-bass
    "mid": (43, 58),     # G2-Bb3 warm round, money register
    "high": (59, 72),    # C4-C5 solo/tenor, bright, effortful
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),
    "tenuto": (72, 0.9),
    "staccato": (64, 0.25),
    "marcato": (92, 0.9),
    "sforzando": (104, 0.7),
    "flutter": (75, 1.0),
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # harmonic-rich — conical bore brass
    "mod_freq_ratio": 1.0,      # 1:1 FM, brass-like spectrum
    "mod_depth": 2.0,           # darkest of brass — fewer strong upper harmonics
    "attack": 0.06,             # large mouthpiece speaks slow (30-70 ms)
    "release": 0.16,
}

# Production defaults
REVERB_TAIL = 1.5       # seconds, hall — short tail keeps low-end definition
EQ_BODY = (200, -2.5)   # peaking cut Hz, dB — clear mud/boxiness
EQ_PRESENCE = (1200, 2.0)  # peaking boost Hz, dB — tuba presence/definition
EQ_AIR = (4000, 1.5)    # highshelf Hz, dB — least air of brass
PAN = 0.0               # center for solo/root; -0.2..-0.3 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
