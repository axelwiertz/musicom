# -*- coding: utf-8 -*-
"""Tenor Saxophone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 66
GM_NAME = "Tenor Saxophone"
# RenderPipeline stem label: GM_PROGRAMS[66] = "Tenor Sax" -> stem file
# trackXX_Tenor_Sax.wav (label is "Tenor_Sax", NOT "Saxophone" — match on this)
STEM_LABEL = "Tenor_Sax"

# MIDI ranges (sounding/concert pitch, Bb tenor sax)
RANGE_MIN = 44      # Ab2 (concert; written Bb2 — lowest note on standard horn)
RANGE_MAX = 88      # E6 (concert; altissimo territory ~written F#6)
SOLO_RANGE = (48, 82)   # D3-Ab5 practical solo range
SWEET_SPOT = (53, 78)   # F3-F5 warm singing tenor register, full round tone

# Register zones
ZONES = {
    "low": (44, 53),     # Ab2-F3, dark breathy bottom — husky, fat, less projection
    "mid": (54, 68),     # F#3-C5, warm vocal core — the money register (Coltrane, Rollins)
    "high": (69, 88),    # C#5-E6, bright cutting top — altissimo scream territory
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (80, 1.0),     # smooth vocal tenor — the sax default
    "tenuto": (72, 0.9),     # slight separation, expressive
    "staccato": (65, 0.25),  # short crisp articulation (heavier reed than alto)
    "accent": (92, 0.9),     # sharp reed attack, punchy
    "growl": (78, 1.0),      # reed growl/overblow, dirty blues/rock yell
    "vibrato": (78, 1.0),    # wide deliberate vibrato — the sax hallmark
    "subtoned": (55, 1.2),   # breathy subtone whisper — classic jazz tenor (Ben Webster, Coltrane ballads)
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical bore single reed: even+odd harmonics
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 3.0,           # deeper than alto (2.8) — the tenor's huskier, grittier core
    "attack": 0.05,             # breathy reed onset (40-60 ms, heavier reed than alto)
    "release": 0.10,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, hall — similar to alto, keep articulation clarity
EQ_BODY = (400, -2.5)   # peaking cut Hz, dB — clear boxiness/honk (tenor darker than alto)
EQ_PRESENCE = (2200, 2.5)  # peaking boost Hz, dB — reed core presence (lower than alto 2500 — darker)
EQ_AIR = (5500, 1.5)    # highshelf Hz, dB — breathy air, lower than alto (6000) for warmth
PAN = 0.0               # center for solo lead; +0.2..+0.35 in horn section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)