# -*- coding: utf-8 -*-
"""English Horn (Cor Anglais) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 69
GM_NAME = "English Horn"
# RenderPipeline stem label: GM_PROGRAMS[69] = "English Horn"
# FluidR3 preset 69 = "English Horn" (exact match, no quirk)
STEM_LABEL = "English_Horn"

# MIDI ranges (sounding pitch, tenor oboe in F)
RANGE_MIN = 50        # D3 (sounding, lowest extended range)
RANGE_MAX = 85        # C#6 (sounding, upper boundary of FluidR3 preset 69)
SOLO_RANGE = (52, 77) # E3-F5 (standard orchestral solo compass)
SWEET_SPOT = (57, 72) # A3-C5 (pastoral, plaintive singing register, New World Largo)

# Register zones
ZONES = {
    "low": (50, 56),        # D3-G#3, deep dark husky velvety double-reed drone
    "sweet_spot": (57, 72), # A3-C5, plaintive singing solo voice
    "mid_high": (73, 79),   # C#5-G5, intense expressive penetrating melodic lines
    "altissimo": (80, 85),  # G#5-C#6, thin pinched dramatic top
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.05),
    "espressivo": (85, 1.10),
    "tenuto": (72, 0.90),
    "staccato": (65, 0.30),
    "accent": (94, 0.85),
    "pianissimo": (52, 1.00),
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical double reed: even + odd harmonic series
    "mod_freq_ratio": 1.0,      # fundamental-locked reed excitation
    "mod_depth": 2.2,           # warm & round double reed (darker than soprano oboe 2.5)
    "attack": 0.06,             # reed onset inertia (40-70 ms)
    "release": 0.12,            # natural breath release
}

# Production defaults
REVERB_TAIL = 2.2           # seconds, concert hall acoustic space
EQ_BODY = (600, 2.0)        # peaking boost Hz, dB — warm pear-bell resonance
EQ_PRESENCE = (2200, 2.0)   # peaking boost Hz, dB — expressive double-reed formant
EQ_AIR = (8000, -1.0)       # highshelf Hz, dB — gentle high damping for dark pastoral warmth
PAN = 0.10                  # slightly right of center in standard woodwind section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
