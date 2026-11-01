# -*- coding: utf-8 -*-
"""Acoustic Bass (GM32) — musicom instrument constants.

GM32 = Acoustic Bass, the upright double bass played pizzicato — the jazz
walking-bass / folk-bluegrass / rockabilly slap voice. The same instrument
as the orchestral Contrabass (GM43) but in its PIZZICATO idiom: finger-plucked
gut/steel strings over a huge wooden body, fundamental-rich woody thump,
long ring. The GM32 patch is the acoustic (non-amplified) voice; GM33 Electric
Bass (finger) is the amplified magnetic-pickup cousin; GM35 Fretless is the
frets-pulled electric; GM38 Synth Bass 1 is the oscillator voice. GM32 is the
one with NO electronics in the signal path.

Reference range for the standard 4-string upright (E1–G4, tuned E1 A1 D2 G2):
MIDI 28–67; 5-string adds low B0 (23). The GM patch (FluidR3 preset 32)
spans wider — verified by empirical sweep (see REPORT.md).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 32
GM_NAME = "Acoustic Bass"
# RenderPipeline stem label: GM_PROGRAMS[32] = "Acoustic Bass" -> sanitized
# trackXX_Acoustic_Bass.wav (FluidR3 preset 32 = "Acoustic Bass" — match)
STEM_LABEL = "Acoustic_Bass"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — 5-string low B0 (23) sits one semitone below;
                     #   GM patch floor (empirical sweep)
RANGE_MAX = 72       # C5 — practical ceiling: above here the upright turns
                     #   thin and loses the woody body (not idiomatic)
SOLO_RANGE = (36, 60)   # C2–C4 — walking-bass pocket where the pizz speaks
                        #   clearly without mud
SWEET_SPOT = (40, 57)   # E2–A3 — the jazz walking zone: root-fifth fills,
                        #   broken octaves, the characteristic woody thump

# Register zones
ZONES = {
    "sub": (24, 35),       # C1–E2 — open-string/pedal zone: chest thump,
                           #   felt more than heard, single notes only
    "walking": (36, 52),   # C2–E3 — PRIMARY register: jazz walking bass,
                           #   root-fifth lines, bluegrass half-notes
    "mid": (53, 64),       # F3–E4 — melodic fills, bowed-adjacent pizz
                           #   solos, singing woody tone
    "high": (65, 72),      # F4–C5 — thumb-position territory: thin,
                           #   cello-like, exposed solos only
}

# Articulation defaults (velocity, duration_factor)
# Acoustic bass pizz vocabulary: the jazz lexicon — walking, thump, slap.
ARTICULATIONS = {
    "pizz": (74, 1.0),        # default finger pluck — round, woody, the voice
    "walking": (72, 0.95),    # quarter-note walking pulse — even, detached
    "slap": (96, 0.30),       # rockabilly string slap — percussive thwack,
                              #   string hits fingerboard (the signature)
    "ghost": (38, 0.15),      # dead-note left-hand damp — groove filler
    "legato": (70, 1.0),      # slurred pizz / hammer — connected line
    "slide": (64, 1.10),      # glissando up/down — fingered slide, woody
    "arco": (78, 1.0),        # bowed (jazz bow) — sustained, reedy, cello-like
    "staccato": (68, 0.35),   # short damped pizz — tight, dry
    "accent": (92, 0.85),     # emphatic downbeat pluck
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"     # sound/synthesis/karplus_strong.py (SP-011)
                          # A plucked string waveguide is the physical model:
                          # the loop low-pass IS the wooden-body damping, a
                          # long loop_gain gives the pizz ring.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,   # long ring — the upright's gut/steel strings are
                           #   long and lightly damped; between electric bass
                           #   0.9970 and harp 0.9985 (matching sitar/fretless
                           #   class; the pizz ring is the identity)
    "lowpass_hz": 1600.0,  # darker than the electric bass 2200-fretless:
                           #   the HUGE wooden body rolls the top off into the
                           #   woody thump band — the acoustic-bass signature
    "width": 0.5,          # moderate spread — acoustic bass is mono-ish; a
                           #   little width in the body resonance tail
    "excitation": "pluck",
    "noise_component": 0.02,  # finger noise / string scrape — part of the
                              #   upright idiom (jazz players embrace it)
    "role": "bass",
}

# BowedString is the ARCO-only engine (stick–slip excitation, slow attack,
# cello-like formant) — a jazz-bow pizz substitute, not the default voice.
BOWED_DEFAULTS = {
    "bow_velocity": 0.18,     # slow, sustained bow stroke
    "bow_force": 1.3,         # moderate pressure — woody, not crushed
    "bow_position": 0.20,     # sul tasto-ish: round, few high partials
    "lpf_coef": 0.6,          # waveguide low-pass: dark, cello-like
    "friction_decay": 5.0,
    "attack": 0.14,           # slow bow bite, not a pluck transient
    "release": 0.20,
    "vibrato_rate": 5.2,
    "vibrato_depth": 0.004,
    "role": "bass",
}

# ModalSynth is a weak fallback only (harmonic stack, no body resonance)
MODAL_PRESET = "string"

# Phase-mod alternative (cheap synth-bass approximation, not recommended)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.6,          # gentle — thicken, not buzz
    "attack": 0.010,           # fast pluck transient (no fret click)
    "release": 0.30,
}

# Production defaults
REVERB_TAIL = 1.8        # seconds, room/jazz-club — the upright lives in a
                         #   small wooden room, not a hall; 1.8 s keeps the
                         #   walking line defined (double_bass 1.8 precedent)
EQ_BODY = (220, -2.5)    # peaking cut Hz, dB — clear the 200-250 Hz body
                         #   boxiness/mud (woody thump is LOWER, ~100 Hz)
EQ_PRESENCE = (700, 2.5) # peaking boost Hz, dB — finger attack and string
                         #   noise presence (the pizz "growl" band)
EQ_AIR = (4000, 1.5)     # highshelf Hz, dB — finger scrape / string shimmer
                         #   (upright pizz has no pick click to add it)
PAN = 0.0                # center — acoustic bass is universally mono/centered


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
