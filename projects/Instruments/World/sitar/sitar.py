# -*- coding: utf-8 -*-
"""Sitar — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — SP-011, sound/synthesis/karplus_strong.py). A high loop_gain
(low damping) keeps the partials ringing, which is what produces the
sitar's characteristic sustained, slightly buzzy (jivari) tone. The
PhaseModSynth FM_DEFAULTS below are the alternative "cheap sitar" patch.
"""

MIDI_PROGRAM = 104
GM_NAME = "Sitar"
# RenderPipeline stem label: GM_PROGRAMS[104] = "Sitar" -> stem file
# trackXX_Sitar.wav (matches exactly, no quirk; FluidR3 preset 104 = "Sitar")
STEM_LABEL = "Sitar"

# MIDI ranges (concert sitar, sounding pitch)
RANGE_MIN = 55      # G3 — bottom of kharaj (bass) strings on a Kharaj Pancham setup
RANGE_MAX = 96      # C7 — top of chikari/drone strings, practical ceiling
SOLO_RANGE = (60, 89)   # C4–A6 — solo repertoire focus (vilayat khani 3-octave)
SWEET_SPOT = (62, 84)   # D4–C6 — primary melodic register, fullest jawari buzz

# Register zones
ZONES = {
    "low": (55, 61),     # G3–B3, kharaj bass strings — dark, long meend slides
    "mid": (62, 77),     # D4–G5, jod/baaj melody strings — primary register
    "high": (78, 96),    # G#5–C7, chikari + high melody — bright, thin, cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (78, 1.0),     # standard mizrab (plectrum) stroke — full decay
    "meend": (70, 1.6),     # bent pull across fret — glissando, elongated
    "gamak": (84, 0.35),    # hammer-on oscillation — fast, ornamental
    "chikari": (60, 0.12),  # drone string stroke — short, high, rhythmic
    "mute": (45, 0.15),     # damped/choked stroke — dry, percussive
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # Karplus-Strong plucked waveguide (SP-011)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,    # low damping -> long ringing partials (jivari)
    "width": 0.45,          # slight stereo spread per note
    "role": "lead",
}
MODAL_PRESET = "string"  # modal resonator fallback (generic plucked string)

# Phase-mod alternative patch (cheap sitar)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 2.0,
    "mod_depth": 4.0,
    "attack": 0.002,
    "release": 0.25,
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, hall — sitar loves space (darbar hall)
EQ_BODY = (350, -2.5)   # peaking cut Hz, dB — tame gourd body boxiness
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — jivari buzz + pluck clarity
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — sympathetic-string shimmer
PAN = 0.0               # center for solo; +0.2..0.35 spread for sections


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
