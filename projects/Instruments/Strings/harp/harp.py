# -*- coding: utf-8 -*-
"""Harp — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — sound/synthesis/karplus_strong.py). The harp is the PUREST
plucked instrument in the KB: 47 direct-plucked strings, no fret, no bow,
no keyboard mechanism. loop_gain 0.9985 is the HIGHEST of the plucked set
(sitar 0.9975, koto 0.9970) because a 1.4 m concert-grand low string rings
5–10 s and even nylon treble strings ring 2–3 s before hand damping.

Range is the 47-string concert grand pedal harp: C1–G7 (MIDI 24–103) —
the widest range of any orchestral instrument except the piano. The seven
double-action pedals (D C B E F G A) retune every string of one pitch
class at once — flat / natural / sharp — so the harp is a DIATONIC
instrument per pedal setting: single strings cannot play chromatics;
glissandi run the diatonic (or enharmonically re-tuned) string row.

The ModalSynth 'string' preset is the fallback (harmonic stack, moderate
decay). PhaseModSynth gives a cheap twangy harp. Enharmonic
(two-pitch-class unison, e.g. Cb against B) is the harp's signature
enharmonic-transposition trick and its signature bisbigliando source.
"""

MIDI_PROGRAM = 46
GM_NAME = "Orchestral Harp"
# RenderPipeline stem label: GM_PROGRAMS[46] = "Orchestral Harp" -> stem file
# trackXX_Orchestral_Harp.wav (matches exactly, no quirk; FluidR3 preset 46 =
# "Orchestral Harp", phdr-verified)
STEM_LABEL = "Orchestral_Harp"

# MIDI ranges (sounding pitch; non-transposing, written at concert pitch)
RANGE_MIN = 24      # C1 — lowest string of the 47-string concert grand
RANGE_MAX = 103     # G7 — highest string (G topping the 7th octave)
SOLO_RANGE = (24, 103)  # the full 47-string span is playable solo
SWEET_SPOT = (55, 88)   # G3–E6 — richest gut/nylon register, main melody

# Register zones
ZONES = {
    "low": (24, 47),     # C1–B2 — wire-wound bass strings: dark, huge, rings
                         #   6–10 s; pedal-noise zone; arpeggio roots only
    "mid": (48, 71),     # C3–B4 — gut/nylon principal melodic + arpeggio
                         #   register (the "harp sounds like a harp" zone)
    "high": (72, 103),   # C5–G7 — nylon treble: bright, fast decay, gliss
                         #   sparkle and harmonics live here
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (84, 1.0),        # fingertip pluck (apoyando) — full string ring
    "nail_attack": (96, 0.9),  # nail/plectrum — bright ping, faster decay
    "arpeggio": (72, 0.9),     # rolled chord, 30–60 ms per string
    "glissando": (78, 1.2),    # thumb/drag across strings — the signature
    "bisbigliando": (62, 1.0), # whisper tremolo between two enharmonic
                               #   unisons (e.g. Cb vs B) — shimmering wash
    "harmonic": (60, 0.6),     # palm node touch — flute-like octave bell
    "damp": (50, 0.12),        # palm étouffée — choked dry stop
    "près_de_la_table": (58, 0.8),  # near soundboard — dark, covered tone
    "flat_fermata": (66, 1.0), # flat-hand stopped ring — buzzing slap decay
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"    # sound/synthesis/karplus_strong.py (SP-011)
MODAL_PRESET = "string"  # closest STOCK bank (harmonic stack, moderate
                         #   decay) — the "clean harp" fallback
# Karplus-Strong primary: plucked waveguide = the exact physical model.
# loop_gain 0.9985 — HIGHEST of the plucked set: concert-grand bass strings
# (1.4 m, wire-wound) ring 6–10 s, gut mid strings 3–5 s, nylon trebles
# 2–3 s. Nothing in the KB out-rings a harp bass string except the open
# pedal (no dampers between notes — the harpist damps by hand).
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9985,    # lowest damping of the plucked family: long
                            #   undamped harp ring (sitar 0.9975 is next)
    "width": 0.55,          # wide stereo focus — 47 strings across the body
    "role": "lead",
}

# Modal custom bank for the mid-register pluck (gut string, A4 reference):
# a near-harmonic stack with the string's real slight inharmonicity and the
# long ring. decay is a RATE (higher = faster), so these are very LOW —
# only the timpani/vibraphone class sits lower in the KB.
HARP_MODES = [
    (440.0, 1.00, 0.22),    # f0 (A4) — the tuned pitch, multi-second ring
    (880.0, 0.32, 0.35),    # 2.0x — octave (strong, gut-bright)
    (1320.0, 0.18, 0.55),   # 3.0x — octave + fifth
    (1760.0, 0.10, 0.80),   # 4.0x — two octaves
    (2200.0, 0.05, 1.20),   # 5.0x — pluck-edge shimmer
]

# Phase-mod alternative patch (cheap harp)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,  # the strong octave partial
    "mod_depth": 1.3,       # modest — a harp is mellower than guitar
    "attack": 0.003,
    "release": 1.8,         # harp ring is long even in cheap patches
}

# Production defaults
REVERB_TAIL = 2.4       # seconds, hall — the harp is THE classical hall
                        #   instrument (pedal harp lives on a concert stage);
                        #   longest tail of the plucked set, matches the
                        #   string ensemble context (2.0–2.5 s)
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — tame soundboard boom/mud on
                        #   the big resonant box (largest body in the KB)
EQ_PRESENCE = (3500, 1.5)  # peaking boost Hz, dB — fingertip pluck attack
EQ_AIR = (10000, 2.0)   # highshelf Hz, dB — treble-string shimmer + gliss
                        #   sparkle (harp recordings are air-forward)
PAN = 0.0               # center solo; 0.2–0.35 right in classical orchestra
                        #   seating (audience view), -0.25 if mirrored


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
