# -*- coding: utf-8 -*-
"""Harpsichord — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — sound/synthesis/karplus_strong.py). The harpsichord is a
QUILL-PLUCKED string instrument: each key lifts a jack whose plectrum
plucks one string, so the physical model is a plucked string — the same
family as the harp, sitar, koto and banjo. loop_gain 0.9980 sits between
harp 0.9985 (no dampers at all) and sitar 0.9975: harpsichord strings
ring freely WHILE THE KEY IS HELD (cloth dampers lift off), then stop
fast when the key releases — so scores let notes ring inside the phrase
but the texture is drier than a harp.

Range is the modern concert double-manual harpsichord: F1–F6
(MIDI 29–89), the 61-note standard of 20th-century makers (Dolmetsch/
Challis/Neupert concert doubles). Historic Ruckers/Taskin originals are
shorter (C/E–c''' = 36–84).

The KEY timbre fact: a quill plucks at fixed displacement — TOUCH DOES
NOT CHANGE LOUDNESS. Dynamics on a harpsichord are terraced by
REGISTRATION (choir combinations 16'/8'/8'/4') and ornamented by
agréments, not by velocity. Composition jobs should keep velocities in
a narrow band (84–100) and phrase with articulation + register, the
inverse of the piano lesson.

The ModalSynth 'string' preset is the fallback (harmonic stack,
moderate decay). PhaseModSynth gives a cheap nasal twang. The 4'
(octave) choir is what makes the harpsichord sound like a harpsichord:
a near-harmonic stack DOUBLED one octave up at ~half amplitude.
"""

MIDI_PROGRAM = 6
GM_NAME = "Harpsichord"
# RenderPipeline stem label: GM_PROGRAMS[6] = "Harpsichord" -> stem file
# trackXX_Harpsichord.wav (matches exactly, no quirk; FluidR3 preset 6 =
# "Harpsichord", phdr-verified)
STEM_LABEL = "Harpsichord"

# MIDI ranges (sounding pitch; non-transposing, written at concert pitch)
RANGE_MIN = 29      # F1 — lowest key of the modern concert double
RANGE_MAX = 89      # F6 — highest key of the 61-note concert compass
SOLO_RANGE = (29, 89)  # the full 61-key span is playable solo
SWEET_SPOT = (48, 84)  # C3–C6 — 8' register principal melody + continuo zone

# Register zones
ZONES = {
    "low": (29, 47),     # F1–B2 — 16'/8' bass: continuo bass line, big and
                         #   snarling (the 16' choir only really speaks here)
    "mid": (48, 71),     # C3–B4 — 8' principal register: melody, harmony,
                         #   the "harpsichord sounds like a harpsichord" zone
    "high": (72, 89),    # C5–F6 — 4' octave choir + 8' treble: sparkle,
                         #   ornaments, UPPERWORKS; brilliant but thin solo
}

# Articulation defaults (velocity, duration_factor).
# NOTE the velocity band is NARROW — quill displacement is fixed, so
# velocity mostly changes pluck noise/brightness, not loudness. Terraced
# dynamics come from registration; expression from ornaments.
ARTICULATIONS = {
    "pluck_8ft": (88, 1.0),    # single 8' choir — the neutral harpsichord
    "full_choir": (96, 1.2),   # 16'+8'+8'+4' tutti — forte terrace, fanfare
    "octave_4ft": (78, 0.9),   # 4' alone — thin, nasal, flute-like solo
    "lute_buff": (70, 0.55),   # buff/lute stop — leather/felt muting, nasal
    "arpeggio_broken": (74, 0.9),  # continuo broken-chord bass (the job)
    "trill": (82, 0.5),        # agrement trill — THE harpsichord articulation
    "mordent": (86, 0.3),      # mordent/pince — quick upper-neighbor bite
    "etouffer": (52, 0.15),    # hand-damp / finger stop — choked dry release
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"    # sound/synthesis/karplus_strong.py (SP-011)
MODAL_PRESET = "string"  # closest STOCK bank (harmonic stack, moderate
                         #   decay) — the "clean plucked string" fallback
# Karplus-Strong primary: quill-plucked waveguide = the exact physical model.
# loop_gain 0.9980 — between harp 0.9985 (no dampers) and sitar 0.9975:
# harpsichord strings ring 2–5 s while the key holds (cloth dampers lift),
# bass longer than treble; releasing the key drops the damper fast.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9980,    # between harp 0.9985 and sitar 0.9975 — long
                            #   in-phrase ring, damper-clean releases
    "width": 0.5,           # boxy but focused stereo — smaller soundboard
                            #   than a concert harp, wider than a guitar
    "role": "lead",
}

# Modal custom bank for the mid-register quill pluck (8'+4' choirs, A4
# reference): a near-harmonic stack DOUBLED at the octave (the 4' choir
# is the harpsichord's signature upperwork). decay is a RATE (higher =
# faster), so these are LOW but slightly faster than the harp's
# 0.22–1.20 — the damper rail kills on release.
HARPSICHORD_MODES = [
    (440.0, 1.00, 0.35),    # f0 (A4) — 8' choir fundamental, 2–5 s ring
    (880.0, 0.45, 0.50),    # 2.0x — 8' octave partial
    (880.0, 0.55, 0.35),    # 4' choir fundamental (same f0, octave up)
    (1320.0, 0.22, 0.70),   # 3.0x — 8' octave + fifth (quill twang)
    (1760.0, 0.25, 0.50),   # 4' + 8' 4th partial overlap — brightens
    (2640.0, 0.10, 0.90),   # 4' 3rd partial — nasal pluck edge
]

# Phase-mod alternative patch (cheap twangy harpsichord)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,  # the strong octave (4' choir) partial
    "mod_depth": 2.2,       # nasal/twangy — brighter than the harp's 1.3
    "attack": 0.002,        # quill pluck = nearly instant onset
    "release": 1.4,         # strings stop when the key lifts
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, chamber/baroque hall — harpsichords live
                        #   in smaller resonant rooms than a modern symphonic
                        #   hall (over-tailing washes out the pluck definition)
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame soundboard boxiness
EQ_PRESENCE = (3500, 2.0)  # peaking boost Hz, dB — quill pluck twang clarity
EQ_AIR = (9500, 1.5)    # highshelf Hz, dB — 4' choir upperwork shimmer
PAN = 0.0               # center solo; harpsichord sits right-of-center in
                        #   baroque continuo sections (audience view)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
