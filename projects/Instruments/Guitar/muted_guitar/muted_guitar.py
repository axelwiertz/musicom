# -*- coding: utf-8 -*-
"""Muted Guitar — musicom instrument constants.

GM 28 = Electric Guitar (muted). The palm-muted / fret-hand-damped electric
guitar — a solid-body electric played with the picking hand resting on the
strings just in front of the bridge (palm mute) and/or the fretting hand
relaxed so the strings never ring. The result is the shortest, most
percussive guitar voice: a pitched "chunk" rather than a sustaining note.

This is the DNA of funk rhythm guitar (Jimmy Nolen / Catfish Collins /
Nile Rodgers 16th-note chops), of metal riffing (the palm-muted chug), and
of any arrangement that needs a tight rhythmic guitar that does not smear.

Reference range for the standard 22-fret guitar: MIDI 40-76 (E2-E6).
The GM patch (FluidR3 preset 28 "Palm Muted Guitar") spans 28-84 (E1-C6).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 28
GM_NAME = "Electric Guitar (muted)"
# RenderPipeline stem label: GM_PROGRAMS[28] = "Electric Guitar (muted)"
#   -> stem file trackXX_Electric_Guitar_muted.wav
# FluidR3 preset 28 is named "Palm Muted Guitar" — the SF2 uses the
# instrument name, the pipeline uses the GM2 spec spelling; cosmetic only,
# no routing impact. STEM_LABEL matches the pipeline's real label so
# stem-file lookups work.
STEM_LABEL = "Electric_Guitar_muted"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 28       # E1 — GM patch floor (real guitar low E = 40)
RANGE_MAX = 84       # C6 — GM patch ceiling (real 22-fret ceiling E6 = 76)
SOLO_RANGE = (40, 76)   # E2–E6 — the real neck; palm-mute chugs live at the
                        #   bottom of this (E2/A2), chops in the middle
SWEET_SPOT = (40, 64)   # E2–E4 — the funk/metal rhythm heart: low-string
                        #   chugs, 16th-note chord chops, double stops

# Register zones
ZONES = {
    "low_chug": (28, 47),    # E1–B2 — palm-muted low-E/A chug zone: the
                             #   metal riff and funk "bass-string" chunk;
                             #   fundamental-dominant thump, no ring
    "mid_chop": (48, 64),    # C3–E4 — THE muted-guitar zone: 16th-note
                             #   chord chops, single-note funk lines,
                             #   double stops, scratch textures
    "high": (65, 84),        # F4–C6 — short muted stabs, dead-string
                             #   fills, top-note accents; pitch gets thin
                             #   and clicky above ~E5 — use sparingly
}

# Articulation defaults (velocity, duration_factor)
# Durations are the POINT of this instrument: everything is short. A
# "muted" note that rings for a beat is a contradiction — the palm/fret
# hand kills the string within roughly 50-250 ms.
ARTICULATIONS = {
    "palm_mute": (82, 0.18),   # Default: pick stroke with the palm edge
                               #   resting on the string at the bridge —
                               #   pitched attack, fast decay, no ring
    "chug": (92, 0.08),        # Low-E/A 16th chug — hardest pick, dead
                               #   stop; the metal riff atom (0.08 ≈ 40 ms
                               #   at 120 bpm 16ths)
    "funk_chop": (78, 0.12),   # 16th-note chord chop — short percussive
                               #   stab on the upbeats, the Nile Rodgers
                               #   "chick"; 3-4 note voicings only
    "muted_strum": (72, 0.10), # Full-strum rake, fully damped — a "shhk"
                               #   texture rather than a chord
    "scratch": (38, 0.05),     # Fret-hand dead-string scratch — no defined
                               #   pitch, pure rhythm texture (the "chika")
    "staccato": (80, 0.22),    # Single-note muted lead — pitch IS defined,
                               #   just short; funk/metal single-line fills
    "open_accent": (90, 0.60), # Momentary palm release — chord rings out;
                               #   the contrast accent that makes mutes read
    "double_stop": (76, 0.15), # Two-note muted double stop (root+5th or
                               #   root+octave) — riff punctuation
    "octave": (74, 0.30),      # Octave funk line (Wes-style shape, muted
                               #   articulation) — single-note hook
    "slide": (70, 0.25),       # Muted slide up/down — the fret-hand drag,
                               #   short travel
    "bend": (78, 0.40),        # Short bluesy bend — pitch rise then damped
    "ghost_note": (30, 0.04),  # Near-inaudible 16th filler — grid texture,
                               #   keeps the hand moving between real notes
    "accent": (90, 0.12),      # Hard dig — cutting muted hit on the "1"
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"  # sound/synthesis/karplus_strong.py KSModel
                              # Muted guitar IS still a plucked string, but
                              # with the damping term cranked: palm mute =
                              # a very lossy waveguide loop. Karplus-Strong
                              # captures the pitched-but-dead character in
                              # a way FM/modal cannot.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9850,          # Palm mute kills the ring — ~0.2-0.4 s
                                  #   decay vs 0.9970+ for open strings; the
                                  #   lowest loop gain in the guitar family
    "excitation": "pick",         # Hard plectrum attack — the click IS the
                                  #   funk/metal articulation
    "width": 0.30,                # Narrow pulse = bright pick transient,
                                  #   then the damping eats the tail
    "lowpass_hz": 2200,           # Palm flesh + bridge pickup rolloff —
                                  #   darker than jazz 3500 because the
                                  #   muted string has almost no upper
                                  #   harmonic sustain
    "noise_component": 0.030,     # Moderate: pick scrape + palm slap are
                                  #   part of the sound (vs thumb 0.015)
}

# ModalSynth fallback — string bank with very fast decay rates
MODAL_PRESET = "string"

# PhaseMod alt (cheap muted-guitar emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",       # Even+odd harmonics for string vibration
    "mod_freq_ratio": 1.0,        # Octave doubling
    "mod_depth": 2.0,             # More edge than jazz (1.5) but less than
                                  #   distortion — the pick attack needs bite
    "attack": 0.004,              # Near-instant pick transient
    "release": 0.08,              # Very fast damping — the mute
}

# Production defaults
REVERB_TAIL = 0.9        # seconds, tight dry amp/room — funk and metal
                         # rhythm guitar is deliberately DRY; long tails
                         # blur the 16th-note articulation that defines it
EQ_BODY = (220, -1.5)    # peaking cut Hz, dB — trim low-mid boom from the
                         #   palm-mute thump so chugs don't fight the bass
EQ_PRESENCE = (3200, 2.5) # peaking boost Hz, dB — pick-attack click and
                          #   chop definition; the muted guitar needs this
                          #   to be heard at all (no sustained energy)
EQ_AIR = (8000, 0.5)     # highshelf Hz, dB — very little air: damping and
                         #   palm flesh remove the top by design
PAN = -0.25              # centre-left guitar seat (rhythm guitar doubled
                         #   hard L/R at ±0.6 in funk/metal productions)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
