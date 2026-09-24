# -*- coding: utf-8 -*-
"""Harmonica — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is PhaseModSynth (free-reed
aerophone — sound/synthesis/phase_mod.py). A saw carrier with moderate
modulation reproduces the harmonica's reedy, breathy tone. The harmonica
free reed is the same physical principle as the accordion reed, but smaller
(bass reeds ~10mm, tenor ~7mm, alto ~5mm) with a slightly softer buzz.

Identity: GM22 = Harmonica — covers both diatonic (10-hole, 60-84, most
common in blues/folk/rock) and chromatic (12-16 hole, 48-96). The GM patch
is the chromatic harmonica at full compass, but composition jobs write in
the diatonic sweet spot C4-C6 (60-84) for blues bends or the full chromatic
span for classical/jazz lines.
"""

MIDI_PROGRAM = 22
GM_NAME = "Harmonica"
# RenderPipeline stem label: GM_PROGRAMS[22] = "Harmonica" -> stem file
# trackXX_Harmonica.wav (matches exactly, no quirk; FluidR3 preset 22 =
# "Harmonica")
STEM_LABEL = "Harmonica"

# MIDI ranges (chromatic harmonica, sounding pitch)
RANGE_MIN = 48      # C3 — bottom of 16-hole chromatic (Hohner Super 64)
RANGE_MAX = 96      # C7 — top of 16-hole chromatic; practical ceiling
SOLO_RANGE = (60, 84)   # C4-C6 — 10-hole diatonic sweet spot + chromatic core
SWEET_SPOT = (64, 79)   # E4-G6 — richest register, strongest reed projection

# Register zones
ZONES = {
    "low": (48, 59),     # C3-B3 — chromatic bass reeds: dark, breathy, soft
    "mid": (60, 76),     # C4-E5 — primary melodic register (diatonic core)
    "high": (77, 89),    # F5-F6 — bright, cutting, overblow territory
    "extreme": (90, 96), # G6-C7 — thin, piercing, lowest reed response
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "blow": (74, 1.0),      # standard exhaled note — default attack
    "draw": (68, 1.0),      # inhaled note — slightly softer onset
    "staccato": (75, 0.15), # tongue-stop — quick, percussive
    "shakes": (82, 0.5),    # rapid hand tremolo (wah-wah amplitude mod)
    "bend": (62, 1.6),      # pitch bend down 2-3 semitones — blues expression
    "overblow": (90, 0.25), # extreme reed-bending for high partials
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # free reed = symmetric oscillator: even+odd
                                #   harmonics (like accordion/sax family)
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 2.5,           # moderate — harmonica reed buzz is slightly
                                #   softer than accordion (3.2) but brighter
                                #   than flute (1.5); between oboe (2.5) and
                                #   accordion
    "attack": 0.010,            # near-instant — reed speaks immediately on
                                #   breath onset (faster than accordion 0.015)
    "release": 0.04,            # very fast — reed stops near-instantly on
                                #   breath reversal; the cupped-wah release
                                #   is longer in practice
}
MODAL_PRESET = "string"  # modal fallback: sustained harmonic stack, clean

# Production defaults
REVERB_TAIL = 1.2       # seconds, room — harmonica is dry/close; keep
                        #   breath detail clear, avoid washout
EQ_BODY = (500, -2.0)   # peaking cut Hz, dB — tame cupped-hand boxiness
EQ_PRESENCE = (2000, 3.0)  # peaking boost Hz, dB — reed clarity + bite
EQ_AIR = (7000, 2.0)    # highshelf Hz, dB — breath + overblow shimmer
PAN = 0.0               # center for solo; ±0.2 spread for dual harmonica
                        #   layering (left-right hand separation)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)