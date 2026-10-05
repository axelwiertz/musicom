# -*- coding: utf-8 -*-
"""Soprano Saxophone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM64 = Bb soprano saxophone — the smallest and brightest standard
saxophone (straight conical tube, single reed, highest member of the SATB sax
quartet). Piercing focused tone sits between clarinet and alto sax — it cuts
through any mix as a lead voice. Sounding concert pitch (MIDI notes are concert,
NOT transposed).
"""

MIDI_PROGRAM = 64
GM_NAME = "Soprano Saxophone"
# RenderPipeline stem label: GM_PROGRAMS[64] = "Soprano Sax" -> stem file
# trackXX_Soprano_Sax.wav (label is "Soprano_Sax", NOT "Saxophone" — match on this)
STEM_LABEL = "Soprano_Sax"

# MIDI ranges (sounding/concert pitch, Bb soprano sax)
RANGE_MIN = 54      # Gb3/F#3 (concert; written Ab3 — low note on standard horn)
RANGE_MAX = 89      # F6 (concert; altissimo territory ~written G6)
SOLO_RANGE = (62, 84)   # D4–C6 practical solo range
SWEET_SPOT = (67, 79)   # G4–G5 bright piercing soprano register, cuts through any mix

# Register zones
ZONES = {
    "low": (54, 63),     # Gb3–D#4, reedy closed tone — crisp but thinner than alto
    "mid": (64, 74),     # E4–D5, bright commanding core — the soprano's money register
    "high": (75, 89),    # D#5–F6, piercing screaming top — altissimo intensity, cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (82, 1.0),     # smooth vocal soprano — the sax default, lightest reed
    "tenuto": (74, 0.9),     # slight separation, expressive
    "staccato": (68, 0.22),  # short crisp articulation (lightest fastest reed in sax family)
    "accent": (94, 0.9),     # sharp reed attack, punchy — soprano cuts hardest
    "growl": (80, 1.0),      # reed growl/overblow — dirty altissimo yell (Dirty Dozen Brass Band)
    "vibrato": (80, 1.0),    # wide deliberate vibrato — narrower than alto, faster in classical playing
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical bore single reed: even+odd harmonics
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 2.6,           # between clarinet 2.0 and alto 2.8 — soprano reed is lighter, brighter
    "attack": 0.03,             # lightest fastest reed in the sax family (thinnest reed, 20-40 ms)
    "release": 0.08,            # smallest air column stops fastest
}

# Production defaults
REVERB_TAIL = 1.4       # seconds, hall — shorter than alto 1.6, keep the bright attack defined
EQ_BODY = (800, -2.0)   # peaking cut Hz, dB — clear reed honk/boxiness (higher than alto 400 — soprano is smaller)
EQ_PRESENCE = (2800, 2.5)  # peaking boost Hz, dB — reed core presence (higher than alto 2500 — brighter, cuts more)
EQ_AIR = (6500, 1.5)   # highshelf Hz, dB — breathy air, higher than alto 6000 for shimmer
PAN = 0.0               # center for solo lead; +0.3..+0.45 in sax section (right, panned against baritone left)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)