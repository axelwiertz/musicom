# -*- coding: utf-8 -*-
"""Pizzicato Strings — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — sound/synthesis/karplus_strong.py). Pizzicato is a BOWED-string
instrument played by PLUCKING the string with a fingertip — the excitation
is a finger pluck (flesh, not a plectrum or hammer), so the waveguide is the
exact physical model. loop_gain 0.9960 is deliberately MODERATE: the string
section's pizzicato is a dry, rhythmic sound (upper violin strings barely
sustain at all; only bass/cello pizz ring past ~1 s). It sits between clavi
0.9960 (rubber-muted struck string) and electric bass 0.9970 (wound steel
ring) — the four-string section's low strings are wound steel/gut and carry
the ring; the high strings are the driest thing in the KB. ModalSynth
'string' preset (harmonic stack, impulse excitation) is the clean fallback.

Identity: GM45 = the string SECTION playing pizzicato (plucked, not bowed) —
a rhythmic/ostinato colour voice, NOT a sustain lead. Real-world ceiling:
loudest pizz ≈ mezzo-forte with the bow; the highest decent violin pizz note
is ~C6 (84); above that the tone thins out fast. Section pizz has a natural
looseness in timing — write with a slight rhythmic lift, not machine-grid
perfection. Monophonic per player, but the patch is the section: small
2–4-note chords (division) work; dense orchestration gets messy.
"""

MIDI_PROGRAM = 45
GM_NAME = "Pizzicato Strings"
# RenderPipeline stem label: GM_PROGRAMS[45] = "Pizzicato Strings" -> stem
# file trackXX_Pizzicato_Strings.wav (matches exactly, no quirk; FluidR3
# preset 45 = "Pizzicato Section" — internal SF2 name differs cosmetically,
# no routing impact)
STEM_LABEL = "Pizzicato_Strings"

# MIDI ranges (sounding pitch; the section spans contrabass..violin)
RANGE_MIN = 36      # C2 — GM spec floor (standard GM range C2–C7); the
                    #    section patch reaches the contrabass pizz register
RANGE_MAX = 96      # C7 — GM spec ceiling; above ~C6 (84) violin pizz gets
                    #    progressively thinner, 85–96 is effect/sparkle only
SOLO_RANGE = (48, 84)   # C3–C6 — the "decent pizz" register: section
                        #   samples speak clearly across cello/viola/violin
SWEET_SPOT = (55, 79)   # G3–G5 — balanced middle: cello upper + viola +
                        #   violin mid, round pluck, no thud, no squeak

# Register zones
ZONES = {
    "low": (36, 54),     # C2–F#3 — bass/cello pizz: thick, present, SOME
                         #   sustain; the ostinato/bass-line register (the
                         #   most audible, longest-ringing pizz in the section)
    "mid": (55, 76),     # G3–E5 — viola/violin mid: balanced round pluck,
                         #   accompaniment + countermelody home zone
    "high": (77, 96),    # F5–C7 — violin high: dry, thin, NO sustain;
                         #   sparkle/accent only (above C6=84 very thin)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pizz": (74, 0.35),      # standard finger pluck — dry ring, the default
    "ostinato": (68, 0.20),  # repeated rhythmic figure — the section's bread
                             #   and butter (short, even, rhythmic lift)
    "secco": (58, 0.12),     # choked/staccato stop — very short, dry tick
    "bass_pizz": (82, 0.90), # low-string pluck — thick, full, lets it ring
                             #   (cello/contrabass; l.v. / ring-over)
    "snap": (100, 0.08),     # Bartók snap pizz — hook-under + slap on
                             #   fingerboard: loud, percussive, little pitch
    "left_hand": (52, 0.30), # left-hand pull-off ("LH pizz") — weak, single
                             #   descending notes, pro-section effect only
    "double_stop": (80, 0.40),  # two-string pluck — chord fill (division;
                                #   avoid dense multi-stop section writing)
    "accent": (94, 0.25),    # hard marcato pluck — driving downbeat
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"    # sound/synthesis/karplus_strong.py (SP-011)
MODAL_PRESET = "string"  # ModalSynth '/string' fallback — harmonic stack,
                         #   impulse excitation (clean plucked-string tone)
# Karplus-Strong primary: finger-plucked waveguide = the exact excitation.
# loop_gain 0.9960 — MODERATE: section pizz is the driest plucked family
# member (only low strings ring; high violin strings sustain ~0 s). Between
# clavi 0.9960 (rubber-muted) and electric bass 0.9970 (wound steel ring).
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,    # dry finger pluck: 0.3–1.5 s ring, bass strings
                            #   longest, upper strings shortest in the KB
    "excitation": "pluck",  # fingertip flesh — rounder, softer than a pick
    "width": 0.55,          # section spread (10+ players, slight detune)
    "lowpass_hz": 7500,     # wooden body warmth — pizz is NOT a glassy
                            #   pluck; cut the harsh string edge
    "noise_component": 0.03,  # finger-flesh contact noise on the attack
    "role": "accent",
}

# Phase-mod alternative patch (cheap pizz, not recommended)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.0,  # fundamental-locked pluck
    "mod_depth": 1.2,       # modest — mellow finger pluck
    "attack": 0.002,        # near-instant fingernail/flesh onset
    "release": 0.20,        # short, dry cutoff
}

# Production defaults
REVERB_TAIL = 2.0       # seconds, hall — pizz lives in the orchestra but the
                        #   verb must NOT smear the pluck transient; 2.0 s
                        #   hall (same as violin) is the ceiling
EQ_BODY = (300, -2.5)   # peaking cut Hz, dB — tame section body boxiness
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — fingertip wood+string
                           #   attack presence ("pluck" band)
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — subtle string sparkle; keep
                        #   gentle — high violin pizz is already thin
PAN = 0.0               # center solo; -0.15..-0.25 section seating in
                        #   classical orchestra (strings stage-left)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)