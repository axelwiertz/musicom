# -*- coding: utf-8 -*-
"""Baritone Saxophone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 67
GM_NAME = "Baritone Saxophone"
# RenderPipeline stem label: GM_PROGRAMS[67] = "Baritone Sax" -> stem file
# trackXX_Baritone_Sax.wav (label is "Baritone_Sax", NOT "Saxophone" — match on this)
STEM_LABEL = "Baritone_Sax"

# MIDI ranges (sounding/concert pitch, Eb baritone sax)
RANGE_MIN = 36       # C2 (concert; written Eb2 — low A on standard horn with extension)
RANGE_MAX = 80       # G5 (concert; altissimo territory ~written B5)
SOLO_RANGE = (42, 72)   # F2-C5 practical solo range
SWEET_SPOT = (48, 65)   # C3-F4 warm singing baritone register, deep round tone

# Register zones
ZONES = {
    "low": (36, 47),     # C2-B2, dark rumbling bottom — tuba-like depth, fat chest wall
    "mid": (48, 60),     # C3-C4, warm vocal woody core — the money register
    "high": (61, 80),    # C#4-G5, bright cutting altissimo — punchy accent, scream territory
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.0),     # smooth vocal bari — the sax default, heaviest reed
    "tenuto": (70, 0.85),    # slight separation, expressive
    "staccato": (64, 0.25),  # short crisp articulation (heaviest reed in family)
    "accent": (94, 0.9),     # sharp reed attack, punchy "bari bark"
    "growl": (78, 1.0),      # reed growl/overblow, dirty R&B yell
    "vibrato": (78, 1.0),    # wide deliberate vibrato — slightly slower than tenor
    "subtoned": (55, 1.2),   # breathy subtone whisper — Gerry Mulligan ballad voice
    "slap_tongue": (88, 0.05),  # percussive reed slap — extended technique, bari specialty
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical bore single reed: even+odd harmonics
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 3.2,           # deeper than tenor (3.0) — the bari's even thicker, darker reed core
    "attack": 0.07,             # breathy reed onset (60-80 ms, heaviest reed in the sax family)
    "release": 0.12,            # massive air column takes slightly longer to stop
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, hall — slightly longer than tenor to bloom the low end
EQ_BODY = (400, -3.0)   # peaking cut Hz, dB — clear boxiness/bari honk (deeper than tenor -2.5)
EQ_PRESENCE = (1600, 2.5)  # peaking boost Hz, dB — bari bark core (lower than tenor 2200 — darker)
EQ_AIR = (5000, 1.5)    # highshelf Hz, dB — breathy air, lower than tenor (5500) for warmth
PAN = 0.0               # center for solo lead; -0.2..-0.35 in horn section (left side)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)