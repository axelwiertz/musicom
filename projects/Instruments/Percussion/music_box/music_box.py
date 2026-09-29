# -*- coding: utf-8 -*-
"""Music Box — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM10 Music Box — mechanical pinned-cylinder lamellophone
(steel-comb teeth plucked by pins on a revolving cylinder). The iconic
toy/jewellery-box tinkle.

Channel quirk: must use a melodic channel (0-9) with program 10 —
channel 9 triggers the drum-kit map and the program-0 fallback label
"Acoustic_Grand_Piano".

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — sound/synthesis/modal.py). The steel tine is a CANTILEVER
(clamped at the comb block, free at the tip), not a free-free beam. The
stock 'bell' preset is the closest generic match. A custom bank (MUSIC_BOX_MODES)
with near-harmonic ratios 1:2:3:4 and fast decay rates 3-12 models the
true steel-tine spectrum.

Line-instrument quirk: music box is a MONOPHONIC mechanical instrument —
write single-note melody lines, NOT chords.
"""

MIDI_PROGRAM = 10
GM_NAME = "Music Box"
# RenderPipeline stem label: GM_PROGRAMS[10] = "Music Box" -> stem file
# trackXX_Music_Box.wav (matches exactly, no quirk; FluidR3 preset 10 =
# "Music Box")
STEM_LABEL = "Music_Box"

# MIDI ranges (sounding pitch; standard 72-note movement compass)
# Most common: 18-note movements C5-A6 (72-93). Larger 30/50/72-note
# movements extend down to C4 (60). The GM patch spans the full chromatic
# range, though real boxes below C4 are rare and mushy.
RANGE_MIN = 60       # C4 — bottom of large 72-note movements
RANGE_MAX = 96       # C7 — top of the mechanical compass
SOLO_RANGE = (60, 84)   # C4-C6 — the idiomatic music-box register
SWEET_SPOT = (72, 84)   # C5-C6 — the classic tinkle octave

# Register zones
ZONES = {
    "low": (60, 71),     # C4-B4, dark delicate bass tines, soft attack
    "mid": (72, 84),     # C5-C6, bell-like singing — the classic music-box voice
    "high": (85, 96),    # C#6-C7, thin bright tinkle, short ring
}

# Articulation defaults (velocity, duration_factor)
# Real music boxes have NO velocity control — the pin always plucks at
# fixed displacement. These are creative affordances for composition.
ARTICULATIONS = {
    "pluck": (82, 1.0),       # standard pin strike — the default mechanical tooth
    "soft": (60, 1.0),        # gentle pin — delicate, pillow-soft
    "accent": (100, 0.9),     # harder pin emphasis — brighter, more partials
    "staccato": (70, 0.2),    # short pluck — abrupt mechanical cut-off
    "roll": (74, 0.06),       # rapid repeat (perceived sustain on long notes)
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "bell"    # closest stock bank (generic metallic resonator)
                         # Use MUSIC_BOX_MODES for the exact steel-tine voice

# Custom music box modes: struck cantilever steel tine.
# The tine is clamped at one end (the comb block) and free at the tip.
# An ideal rectangular cantilever has mode ratios ~1 : 6.27 : 17.5 : 34.4
# but the short, thick, tuned tine of a music box is better approximated
# by a NEAR-HARMONIC stack (1:2:3:4) with fast decay — the tine is
# deliberately tuned to a specific pitch, suppressing inharmonicity.
# (freq, amp, decay) — decay RATE (higher = faster). Steel tines ring
# for ~0.3-1.2 seconds (short to moderate, faster than vibraphone's
# aluminium bars, comparable to glockenspiel's steel bars but with a
# softer attack).
MUSIC_BOX_MODES = [
    (440.0, 1.00, 4.0),    # f0 (A4 reference) — the tuned pitch
    (880.0, 0.50, 6.0),    # 2x — octave, warm bloom
    (1320.0, 0.20, 9.0),   # 3x — twelfth, bright overtone
    (1760.0, 0.08, 12.0),  # 4x — double octave, transient ring
]

# Karplus-Strong fallback (the tine IS plucked — waveguide model fits)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9950,    # moderate ring (~0.5-1.0s) — steel tine, shorter
                            #   than guitar 0.997, between kalimba 0.994 and
                            #   banjo 0.996; the short stiff tine decays faster
                            #   than a wound string
    "width": 0.15,          # narrow (single tine = monophonic)
    "role": "melody",
}

# Phase-mod alternative patch (FM bell — clean but sterile)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,   # first overtone
    "mod_depth": 1.2,
    "attack": 0.002,         # near-instant pin release
    "release": 0.3,
}

# Production defaults
REVERB_TAIL = 1.5       # seconds — intimate room/plate, NOT cathedral;
                        #   the mechanical tick is part of the charm
EQ_BODY = (500, -2.0)   # peaking cut Hz, dB — remove boxy case resonance
EQ_PRESENCE = (4000, 2.0)  # peaking boost Hz, dB — tinkle "zing"
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — subtle air for shimmer
PAN = 0.0               # center (solo); music box is inherently mono
                        #   sitting on a table/dresser


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)