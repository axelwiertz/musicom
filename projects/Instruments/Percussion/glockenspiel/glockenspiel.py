# -*- coding: utf-8 -*-
"""Glockenspiel — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with preset='bell' or custom GLOCKENSPIEL_MODES bank.
Glockenspiel bars are steel (tuned metallic bar), with bright inharmonic partials
and moderate/long ring (unlike the dry rosewood of xylophone). The stock 'bell'
preset models high inharmonic metallic resonance well.
Karplus-Strong (loop_gain 0.9980) or PhaseModSynth (mod_ratio 3.5, mod_depth 1.8)
serve as secondary fallbacks.

Identity: GM9 = Glockenspiel (steel bars, hard brass/plastic mallets, non-resonated
case). Sounding range is G5 to C8 (MIDI 79–108), typically written two octaves lower
(G3 to C6 / MIDI 55–84). In musicom standard MIDI notation, sounding pitch is used
(RANGE_MIN=79, RANGE_MAX=108), but GM SoundFonts like FluidR3 respond down to MIDI 55
to support transposed scores.
"""

MIDI_PROGRAM = 9
GM_NAME = "Glockenspiel"
# RenderPipeline stem label: GM_PROGRAMS[9] = "Glockenspiel" -> stem file
# trackXX_Glockenspiel.wav (matches exactly, no quirk; FluidR3 preset 9 =
# "Glockenspiel")
STEM_LABEL = "Glockenspiel"

# MIDI ranges (standard 2.5-octave orchestral glockenspiel)
# Sounding pitch: G5 (79) to C8 (108).
# FluidR3 GM patch supports sounding pitch and octave-transposed (down to 55).
RANGE_MIN = 79       # G5 (sounding) — lowest bar of standard 2.5-octave orchestra bells
RANGE_MAX = 108      # C8 (sounding) — top bar of standard orchestra bells
SOLO_RANGE = (84, 103)   # C6–G7 — core solo / melodic ring register
SWEET_SPOT = (84, 100)   # C6–E7 — brightest crystalline bell chime

# Register zones (sounding pitches)
ZONES = {
    "low": (79, 86),      # G5–D6 — warm metallic chime, longer decay
    "mid": (87, 98),      # D#6–D7 — brilliant crystalline ring, primary melody
    "high": (99, 108),    # D#7–C8 — piercing silver ping, short metallic attack
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "hard_mallet": (88, 1.0),     # brass or hard plastic mallet — crystalline attack
    "soft_mallet": (68, 1.2),     # rubber/wood mallet — mellow metallic chime
    "staccato": (80, 0.4),        # hand-damped or quick stroke — tight metallic ping
    "double_stop": (76, 1.0),     # two mallets struck together — shimmering dyad
    "glissando": (72, 0.3),       # quick mallet sweep across high steel bars
}

# Synthesis engine recommendation
SYNTHESIS = "modal"   # ModalSynth impulse-excited resonator bank
MODAL_PRESET = "bell"  # Built-in stock preset in sound/synthesis/modal.py

# Custom modal modes for steel bar (clamped-free bar / plate inharmonicity)
# f0 (fundamental), ~2.71 (second partial), ~5.15 (third partial), ~8.43
GLOCKENSPIEL_MODES = [
    (1046.5, 1.00, 2.5),    # C6 fundamental — clear ringing tone, slow decay
    (2836.0, 0.50, 4.0),    # ~2.71x — high metallic inharmonic clang
    (5389.0, 0.25, 6.5),    # ~5.15x — brittle shimmer partial
    (8822.0, 0.12, 9.0),    # ~8.43x — silver attack transient
]

# Karplus-Strong fallback
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9980,    # long metallic ring (~1.5-2.5s)
    "width": 0.35,          # stereo width for bell table
    "role": "lead",
}

# Phase-mod alternative patch (FM bell / chime)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.5,  # inharmonic bell ratio
    "mod_depth": 1.6,
    "attack": 0.001,
    "release": 1.5,
}

# Production defaults
REVERB_TAIL = 2.2         # seconds — glockenspiel blooms beautifully in concert hall reverb
EQ_BODY = (800, -2.0)     # dip boxy mid-clash if needed
EQ_PRESENCE = (3500, 2.0) # boost crystalline mallet impact
EQ_AIR = (10000, 2.5)     # high metallic air shimmer
PAN = 0.20                # slightly off-center right in orchestral layout


def midi_to_freq(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
