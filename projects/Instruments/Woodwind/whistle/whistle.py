# -*- coding: utf-8 -*-
"""Whistle — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the tin whistle / penny whistle is an open-tube fipple flue
aerophone (all harmonics present). PhaseModSynth is the primary recommendation
(sine carrier + sine modulator at depth 1.5 captures the bright open-tube
whistle tone — between the pure ocarina 0.8 and breathy shakuhachi 2.0;
attack 0.04 s = fast fipple onset). Additive is the alternative (full harmonic
stack with strong 2nd partial).

Identity: GM78 = tin whistle / penny whistle (Irish/Celtic folk whistle), NOT
a slide whistle or orchestral whistle. Standard D whistle range D4-D6 (62-86)
with overblow to A6 (93). Monophonic breath line — no chords.
"""

MIDI_PROGRAM = 78
GM_NAME = "Whistle"
# RenderPipeline stem label: GM_PROGRAMS[78] = "Whistle" -> stem file
# trackXX_Whistle.wav (matches exactly, no quirk; FluidR3 preset 78 = "Whistle")
STEM_LABEL = "Whistle"

# MIDI ranges (standard D tin whistle, sounding pitch; 2 octaves + overblow)
RANGE_MIN = 62      # D4 — bottom of standard D whistle (low D)
RANGE_MAX = 93      # A6 — overblow top (skilled players go to ~A6)
SOLO_RANGE = (67, 86)   # G4–D6 — folk melody repertoire (jigs/reels/hornpipes)
SWEET_SPOT = (67, 86)   # G4–D6 — brightest, clearest, best projection

# Register zones
ZONES = {
    "low": (62, 69),     # D4–A4 — 1st octave, round flute-like tone
    "mid": (70, 79),     # A#4–G5 — 2nd octave start, bright sweet folk zone
    "high": (80, 93),    # G#5–A6 — 2nd octave top + overblow, piercing
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.0),     # smooth slurred breath, connected notes
    "staccato": (65, 0.18),  # tongued stop — quick, clean articulation
    "cut": (76, 0.06),       # grace note cut — fast higher finger dab
    "roll": (72, 0.15),      # long grace ornament (cran) — rhythmic
    "breath": (55, 0.9),     # soft half-blown, airy tone
    "accent": (92, 0.85),    # hard tongue strike — percussive, driving
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"  # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",          # fipple edge tone = near-sine carrier
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,            # open tube amplifies fundamental + all harmonics
    "mod_depth": 1.5,                 # moderate — between ocarina 0.8 and shakuhachi 2.0
    "attack": 0.04,                   # fast fipple onset (same as piccolo 0.04)
    "release": 0.10,                  # clean breath cutoff
}
ADDITIVE_DEFAULTS = {
    "harmonic_count": 6,              # open tube — 6 audible harmonics
    "harmonic_weights": [0.9, 0.6, 0.4, 0.2, 0.1, 0.05],  # strong fundamental + 2nd
    "attack": 0.04,
    "release": 0.10,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, room — dry folk whistle (pan flute 2.0 / ocarina 1.6)
EQ_BODY = (500, -2.0)   # peaking cut Hz, dB — reduce honk/boxiness
EQ_PRESENCE = (3000, 2.5)  # peaking boost Hz, dB — fipple edge brightness
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — gentle air, avoid shrill
PAN = 0.0               # center for solo; ±0.2 in ensemble


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)