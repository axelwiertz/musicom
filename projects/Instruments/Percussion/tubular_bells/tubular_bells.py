# -*- coding: utf-8 -*-
"""Tubular Bells (Chimes) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — sound/synthesis/modal.py). Tubular bells are struck BRASS
TUBES (not bars, not strings) — the acoustic excitation is a hammer blow on
a hollow tube, producing a rich, warm bell tone with controlled inharmonic
partials. The tube's free-free bending modes follow ratios near
1 : 2.76 : 5.40 : 8.93 (similar to the glockenspiel steel bar, but the
brass alloy and larger diameter produce a warmer, rounder fundamental — the
"church bell" colour that gives tubular bells their identity). The stock
'bell' preset models a generic metallic bar, not a brass tube; the custom
TUBULAR_BELLS_MODES bank is the exact voice.

Identity: GM14 = Tubular Bells (orchestral chimes) — struck brass tubes
suspended in a rectangular frame, played with a rawhide/synthetic mallet.
The iconic tintinnabuli colour: church-bell sonorities (Tchaikovsky 1812,
Berlioz Symphonie Fantastique WV 48, Mahler Symphony 2 "Resurrection"),
ceremonial/hunting accents, and the Mike Oldfield "Tubular Bells" title
theme. NOT a melodic keyboard percussion (marimba, vibraphone, glockenspiel);
NOT a folk instrument. Limited range (~1.5 octaves), so used sparingly for
colour.

Channel quirk: must use a melodic channel (0-9) with program 14 — channel 9
triggers the drum-kit map.
"""

MIDI_PROGRAM = 14
GM_NAME = "Tubular Bells"
# RenderPipeline stem label: GM_PROGRAMS[14] = "Tubular Bells" -> stem file
# trackXX_Tubular_Bells.wav (matches exactly, no quirk; FluidR3 preset 14 =
# "Tubular Bells")
STEM_LABEL = "Tubular_Bells"

# MIDI ranges (sounding pitch; standard 1.5-octave orchestral chimes set)
# Most common symphonic set: C4 (60) to F5 (78), 18 brass tubes.
# Extended 2-octave sets exist (F3-F5 = 53-77) but are rare.
RANGE_MIN = 60       # C4 — bottom tube of standard 1.5-octave set
RANGE_MAX = 78       # F5+ — top tube (some sets go to G5=79)
SOLO_RANGE = (60, 78)   # C4-F5 — the standard 1.5-octave set
SWEET_SPOT = (60, 72)   # C4-C5 — the fundamental octave; roundest bloom,
                        #   closest to a church bell; above C5 the tubes
                        #   get shorter and the tone thins out

# Register zones (range is narrow — only 1.5 octaves so zones overlap)
ZONES = {
    "low": (60, 66),     # C4-C#5 — deep, full church-bell bloom; the
                        #   classic Tchaikovsky 1812 C4 chime
    "mid": (67, 72),     # D5-C5 — balanced chime tone, the sweet spot
    "high": (73, 78),    # C#5-F5 — thinner, brighter, shorter ring;
                        #   punctuation accents (Berlioz/Saint-Saëns)
}

# Articulation defaults (velocity, duration_factor)
# Tubular bells have ONE stroke type (hammer blow) — velocity/duration
# distinctions exist but the range is narrow.
ARTICULATIONS = {
    "stroke": (84, 1.0),       # standard rawhide mallet — full tube ring;
                               #   the default and only real stroke
    "hard": (96, 0.8),         # harder hammer blow — brighter, slightly
                               #   more upper partials, for cutting through tutti
    "soft": (60, 1.0),         # lighter tap — muted bell colour, mellow
    "roll": (70, 0.06),        # rapid alternation between two tubes or
                               #   fast repeated strokes on one tube
    "muted": (72, 0.2),        # hand-damped — choke the ring short;
                               #   rhythmic accent only
    "accent": (94, 0.9),       # sforzando marcato stroke
}

# Synthesis engine recommendation
SYNTHESIS = "modal"   # ModalSynth impulse-excited resonator bank
MODAL_PRESET = "bell"  # closest stock bank (metallic inharmonic, slow
                       # decay) — use TUBULAR_BELLS_MODES for exact tube

# Custom tubular bell modes: struck free-free brass tube.
# Ratios approximate the real tube's bending-mode spectrum:
# f0 (fundamental), ~2.76x, ~5.40x, ~8.93x — similar to a steel bar
# (glockenspiel 2.71, 5.15, 8.43) but shifted up slightly because brass
# alloy has lower Young's modulus + the tube is hollow, raising the
# overtone ratios relative to a solid bar.
# (freq, amp, decay) — decay RATE (higher = faster). Brass tubes ring
# for ~1.5-3 seconds (longer than xylophone/glockenspiel, comparable to
# vibraphone's aluminium bars). Decay rates sit between vibraphone
# (0.30-1.10) and marimba (8-20).
TUBULAR_BELLS_MODES = [
    (440.0, 1.00, 0.50),   # f0 (A4 reference) — the tuned pitch, rich
                           #   warm bloom, slow decay
    (1214.4, 0.55, 0.80),  # ~2.76x — strongest inharmonic partial, the
                           #   "bell overtone" (octave + a fifth)
    (2376.0, 0.25, 1.20),  # ~5.40x — bright metallic strike colour
    (3929.2, 0.10, 2.00),  # ~8.93x — transient attack ring, decays fast
]

# Karplus-Strong fallback (tube is struck, not plucked — demoted)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,    # long metallic ring (~1.5-2.5s)
    "width": 0.25,          # narrow stereo (single tube = monophonic)
    "role": "accent",
}

# Phase-mod alternative patch (FM bell — tubular bell chime)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.76,  # the dominant bell overtone
    "mod_depth": 1.8,
    "attack": 0.001,
    "release": 2.0,
}

# Production defaults
REVERB_TAIL = 2.5       # seconds — long hall/church reverb is IDIOMATIC
                        #   for tubular bells; they bloom in a large space
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — tame tube-box resonance
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — hammer attack + bell
                           #   overtone ring
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — brass-tube shimmer
PAN = 0.0               # center solo; chimes sit center rear in orch.
                        #   layout, behind the mallet percussion


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)