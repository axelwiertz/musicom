# -*- coding: utf-8 -*-
"""Oboe — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 68
GM_NAME = "Oboe"
# RenderPipeline stem label: GM_PROGRAMS[68] = "Oboe" (exact, no quirk;
# SF2 preset 68 = "Oboe (Orch)" — cosmetic suffix only)
STEM_LABEL = "Oboe"

# MIDI ranges (sounding pitch, concert oboe)
RANGE_MIN = 52      # Bb3 (oboe lowest note)
RANGE_MAX = 92      # G6 (practical top; altissimo to ~C6=84 common)
SOLO_RANGE = (58, 84)   # Bb3-C6 solo repertoire focus
SWEET_SPOT = (71, 83)   # Bb4-B5 plaintive singing register, projects best

# Register zones
ZONES = {
    "low": (52, 67),     # Bb3-G4, dark thick reedy, softer
    "mid": (68, 76),     # G#4-C5 throat register, thinner transitional
    "high": (77, 92),    # C#5-G6 piercing bright cutting, trademark top
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.0),
    "tenuto": (70, 0.9),
    "staccato": (64, 0.25),
    "accent": (92, 0.9),
    "flutter": (66, 1.0),    # flutter-tongue, rare agitation effect
    "sforzando": (95, 1.0),  # explosive attack, decays to piano
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # double-reed conical bore: even+odd harmonics
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 2.5,           # brighter/nasal than bassoon (2.0), less than brass
    "attack": 0.05,             # double-reed speaks fast-ish (30-80 ms)
    "release": 0.10,
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, hall — woodwind wind column, medium tail
EQ_BODY = (400, -2.0)   # peaking cut Hz, dB — clear nasal boxiness
EQ_PRESENCE = (3000, 2.5)  # peaking boost Hz, dB — the oboe's piercing reed presence
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — reed/breath air, subtle
PAN = 0.0               # center for solo; -0.15..-0.25 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
