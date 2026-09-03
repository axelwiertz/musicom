# -*- coding: utf-8 -*-
"""Koto — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — SP-011, sound/synthesis/karplus_strong.py). The 13 strings of
a koto are plucked with ivory picks (tsume), and the instrument's signature
is the *sawari* — a slightly detuned overtone that beats against the
fundamental (buzz-string effect). In the waveguide that maps to a loop_gain
midway between a bright guitar (0.996) and the sitar's near-infinite ring
(0.9975). The ModalSynth MODAL_PRESET 'string' bank is the alternative
"clean koto" patch (harmonic stack, no detuned partial).

Hirajoshi tuning (D G A D F, low-to-high on the first 5 strings) is the
traditional honkyoku/jiuta scale — composition jobs should treat Koto as a
pentatonic melodic/drone voice, NOT a chromatic harmony instrument.
"""

MIDI_PROGRAM = 107
GM_NAME = "Koto"
# RenderPipeline stem label: GM_PROGRAMS[107] = "Koto" -> stem file
# trackXX_Koto.wav (matches exactly, no quirk; FluidR3 preset 107 = "Koto")
STEM_LABEL = "Koto"

# MIDI ranges (13-string koto, sounding pitch)
RANGE_MIN = 51      # D#3 — bottom of a 13-string koto (D3=50 with tension drop)
RANGE_MAX = 90      # F#6 — practical top; 13-string high string is D6=86
SOLO_RANGE = (57, 84)   # A3–C6 — solo repertoire focus (jiuta/honkyoku)
SWEET_SPOT = (64, 79)   # E4–G5 — brightest twang, best sawari projection

# Register zones
ZONES = {
    "low": (51, 60),     # D#3–C4 — bass strings 13..9 — warm dark, long ring
    "mid": (61, 76),     # C#4–E5 — strings 8..4 — primary melodic register
    "high": (77, 90),    # F5–F#6 — strings 3..1 — bright thin, cuts through
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (78, 1.0),     # standard tsume (ivory pick) stroke — full decay
    "oshi": (84, 1.7),      # left-hand press behind bridge — upward pitch bend,
                            #   elongated; can also carry the buzz (sawari) accent
    "hajiki": (88, 0.4),    # flicked snap — short, bright, ornament
    "arpeggio": (66, 0.25), # strummed across strings (kakute) — rolled chord
    "mute": (44, 0.15),     # damped/palm-choked stroke — dry, percussive
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # Karplus-Strong plucked waveguide (SP-011)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,    # low damping -> long ringing (koto sustain ~3 s);
                            #   below sitar's 0.9975 — no jivari over-ring
    "width": 0.45,          # slight stereo spread per note
    "role": "lead",
}
MODAL_PRESET = "string"  # modal resonator fallback (harmonic stack, clean)

# Phase-mod alternative patch (cheap koto)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 3.0,
    "mod_depth": 2.5,
    "attack": 0.002,
    "release": 0.3,
}

# Production defaults
REVERB_TAIL = 1.4       # seconds, room/hall — koto ring is dry; keep pluck clear
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame paulownia body boxiness
EQ_PRESENCE = (3200, 2.0)  # peaking boost Hz, dB — tsume click + sawari shimmer
EQ_AIR = (8500, 1.0)    # highshelf Hz, dB — subtle air, silk-string warmth
PAN = 0.0               # center for solo; +0.2..0.35 spread for ensembles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
