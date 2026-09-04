# -*- coding: utf-8 -*-
"""Shamisen — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — SP-011, sound/synthesis/karplus_strong.py). The shamisen is a
3-string Japanese lute struck with a large wooden plectrum (bachi). Its
signature is a sharp, percussive attack (wood-on-skin transient) plus the
*sawari* — a sympathetic buzz at the nut that rattles against the string
(a cousin of the koto's sawari). In the waveguide that maps to a loop_gain
LOWER than the koto (0.9970) and sitar (0.9975): ~0.9955 gives the
shamisen's shorter, punchier, dry ring — folk/theatre bite, not darbar
sustain. The ModalSynth MODAL_PRESET 'string' bank is the alternative
"clean shamisen" patch (harmonic stack, no sawari rattle).

Honchoshi open tuning (D-A-D, low to high) is the classical base — the
shamisen is a LINE instrument (min'yo/folk + kabuki theatre), NOT a
chromatic harmony voice. Composition jobs should write monophonic
melodic/ostinato lines with bachi articulation, not dense chords.
"""

MIDI_PROGRAM = 106
GM_NAME = "Shamisen"
# RenderPipeline stem label: GM_PROGRAMS[106] = "Shamisen" -> stem file
# trackXX_Shamisen.wav (matches exactly, no quirk; FluidR3 preset 106 =
# "Shamisen")
STEM_LABEL = "Shamisen"

# MIDI ranges (3-string shamisen, sounding pitch; honchoshi D-A-D)
RANGE_MIN = 45      # A2 — bottom of the thick niagari (1st) string, tension drop
RANGE_MAX = 89      # F6 — practical top of the 3rd (thin) string
SOLO_RANGE = (57, 84)   # A3–C6 — solo repertoire focus (min'yo/jiuta)
SWEET_SPOT = (60, 79)   # C4–G5 — best bachi snap + sawari projection

# Register zones
ZONES = {
    "low": (45, 56),     # A2–G#3 — niagari string — dark, gut thump
    "mid": (57, 75),     # A3–D5 — middle string — primary melodic register
    "high": (76, 89),    # D#5–F6 — 3rd string — bright, thin, cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (80, 1.0),     # standard bachi stroke — sharp attack, natural decay
    "tsubushi": (92, 0.33), # hard bachi slap on the skin head — percussive thump
    "suzume": (86, 0.25),   # grace-note chirp — fast, ornamental
    "uchijime": (60, 0.12), # left-hand damp after pluck — short, dry
    "hikiyose": (72, 1.5),  # bend up ~1-3 semitones — vocal, elongated
    "tremolo": (78, 2.0),   # suki — fast repeated strokes, sustained tension
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # Karplus-Strong plucked waveguide (SP-011)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9955,    # moderate damping -> punchy dry ring (~1-2 s);
                            #   below koto 0.9970 / sitar 0.9975 — folk bite
    "width": 0.40,          # tight focus (narrower than koto's 0.45)
    "role": "lead",
}
MODAL_PRESET = "string"  # modal resonator fallback (generic plucked string)

# Phase-mod alternative patch (cheap shamisen)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 2.5,
    "mod_depth": 3.0,
    "attack": 0.002,
    "release": 0.2,
}

# Production defaults
REVERB_TAIL = 1.2       # seconds, room/short hall — dry rhythmic pluck; keep
                        #   bachi attack clear (koto 1.4 / sitar 2.2 for contrast)
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame body boxiness
EQ_PRESENCE = (2800, 2.0)  # peaking boost Hz, dB — bachi snap + sawari rattle
EQ_AIR = (8000, 1.0)    # highshelf Hz, dB — subtle air, keep twang not harsh
PAN = 0.0               # center for solo; +0.2..0.3 spread for ensembles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
