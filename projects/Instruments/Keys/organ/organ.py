# -*- coding: utf-8 -*-
"""Organ (Church) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 19
GM_NAME = "Church Organ"
# RenderPipeline stem label: GM_PROGRAMS[19] = "Church Organ" -> stem file
# trackXX_Church_Organ.wav (matches, no quirk; SF2 preset 19 = "Church Organ")
STEM_LABEL = "Church_Organ"

# MIDI ranges (sounding pitch, pipe organ ranks / Hammond 61-key manual)
RANGE_MIN = 36      # C2 (61-key manuals; full AGO pedal C2=36, 32' rank C1=24)
RANGE_MAX = 96      # C7 (top of 61-key manual; 2' rank to G7=103)
SOLO_RANGE = (48, 84)   # C3-C6 solo repertoire focus (two manuals)
SWEET_SPOT = (55, 79)   # G3-G5 — full chorus + solo stops speak best

# Register zones
ZONES = {
    "low": (36, 47),     # C2-B2, pedal/foundation 16'+8', ground the bass
    "mid": (48, 66),     # C3-G#4, diapason/principal chorus, comping + pad
    "high": (67, 96),    # A4-C7, solo reed/mixture, bright and cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (78, 1.0),      # continuous wind — full length, no decay
    "legato": (72, 1.0),       # keys overlapped, seamless
    "staccato": (60, 0.25),    # key release — pipe speaks then stops instantly
    "accent": (92, 0.9),       # swell-pedal emphasis, full drawbars
    "pulse": (68, 0.5),        # rhythmic chord stab / gospel organ vamp
    "trill": (64, 0.125),      # two-note trill, very fast repeats
}

# Synthesis engine recommendation
SYNTHESIS = "additive"     # sound/synthesis/additive.py SoundWave
ADDITIVE_HARMONICS = {
    # Drawbar-style harmonic mix: fundamental 8', 4' (2x), 2 2/3' (3x),
    # 2' (4x), 1 3/5' (5x) — full registrations add 5 1/3' (1.5x) and 1 1/3' (6x)
    "full": [1.0, 0.8, 0.6, 0.5, 0.35, 0.25, 0.15],
    "diapason": [1.0, 0.5, 0.3, 0.15, 0.1, 0.0, 0.0],
    "flute": [1.0, 0.25, 0.05, 0.0, 0.0, 0.0, 0.0],
}
# PhaseModSynth alternative (FM organ, DX7 16'+/8'/4' style)
FM_DEFAULTS = {
    "carrier_shape": "sine",     # sine carriers per drawbar partial
    "mod_freq_ratio": 2.0,       # 2nd partial pair — DX7 organ staple
    "mod_depth": 2.5,
    "attack": 0.005,             # near-instant key-on (organ has no attack)
    "release": 0.05,             # key-off cut — no tail
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, cathedral — long tail is the organ sound
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — clear mud in low-mid
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — chiff/reed presence
EQ_AIR = (7000, 1.0)    # highshelf Hz, dB — subtle air, organ is not bright
PAN = 0.0               # center; +0.3..0.5 split manuals L/R for wide pad


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
