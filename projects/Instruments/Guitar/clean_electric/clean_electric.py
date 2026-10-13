# -*- coding: utf-8 -*-
"""Clean Electric Guitar — musicom instrument constants.

GM 27 = Electric Guitar (clean). The solidbody electric guitar played through a
clean amplifier — the classic rhythm-section chord/strum/arpeggio voice for pop,
rock, funk, country, and R&B. Six strings, magnetic pickups, pick/finger attack.

Reference range for the standard 22-fret guitar: MIDI 40–76 (E2–E6).
The GM patch (FluidR3 preset 27) spans wider, 28–84 (E1–C6).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 27
GM_NAME = "Electric Guitar (clean)"
# RenderPipeline stem label: GM_PROGRAMS[27] = "Electric Guitar (clean)"
#   -> stem file trackXX_Electric_Guitar_clean.wav (matches pipeline label;
#   FluidR3 preset 27 = "Clean Guitar" — internal SF2 name differs cosmetically,
#   no routing impact)
STEM_LABEL = "Electric_Guitar_clean"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 28       # E1 — GM patch floor (real guitar E2=40)
RANGE_MAX = 84       # C6 — GM patch ceiling (real 22-fret ceiling E6=76)
SOLO_RANGE = (43, 76)   # G2–E6 — idiomatic lead zone: single-note lines,
                         #   melodic fills, pick/finger attack
SWEET_SPOT = (52, 72)   # E3–C5 — rich fundamental, best projection for
                         #   chord rhythm and melodic lines

# Register zones
ZONES = {
    "low_strings": (28, 47),    # E1–B2 — bass/fundamental zone: open-string
                                #   roots (E, A, D), palm-muted chugs, low
                                #   chord roots
    "mid": (48, 64),            # C3–E4 — neck pickup warmth: full chords,
                                #   fingerpicking centre (G, B strings)
    "high": (65, 84),           # F4–C6 — bridge pickup: bright, thin,
                                #   cutting single-note leads, treble chords
}

# Articulation defaults (velocity, duration_factor)
# Clean electric guitar articulations map to pick/finger techniques
ARTICULATIONS = {
    "pick_down": (80, 0.20),     # Plectrum downstroke — bright attack,
                                 #   ringing sustain, the default electric
                                 #   articulation
    "pick_up": (70, 0.18),       # Plectrum upstroke — lighter, less percussive
    "finger": (65, 1.0),         # Fingertip pluck — warm, round, mellow
    "palm_mute": (50, 0.12),     # Edge-of-hand damped — short percussive chug,
                                 #   the #1 rhythm technique in rock/punk/funk
    "strum_down": (78, 0.22),    # Full down-strum — multi-string rhythm chord,
                                 #   ringing sustain (the "whoosh" of strings
                                 #   swept by a pick)
    "strum_up": (68, 0.18),      # Lighter up-strum — chord rhythm accent
    "hammer_on": (75, 0.5),      # Legato slur upward — connecting notes
                                 #   without picking, smooth line
    "pull_off": (65, 0.5),       # Legato slur downward — connecting notes
                                 #   without picking
    "slide": (72, 0.8),          # Fret slide — continuous pitch glide,
                                 #   audible fretwire
    "bend": (82, 0.9),           # String bend — pitch rise, increased sustain
    "vibrato": (70, 0.9),        # Whammy bar or finger vibrato
    "harmonic": (90, 0.35),      # Natural/artificial overtone — bell-like
                                 #   chime (12th/7th/5th fret natural harmonics)
    "arpeggio": (62, 0.15),      # Fingerpicked rolled chord — fluid texture
    "ghost_note": (45, 0.08),    # Pick stops on string — percussive scratch,
                                 #   no defined pitch (funk ghost note)
    "accent": (96, 0.20),        # Hard pick dig — cutting downbeat accent
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"  # sound/synthesis/karplus_strong.py KSModel
                              # Clean electric IS a plucked stiff steel string
                              # with magnetic pickup — Karplus-Strong waveguide
                              # is the exact physical model for the string
                              # vibration, simpler than full physical-modelling.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,         # Steel strings ring 1–3 s; between clavi
                                 #   0.9960 and steel_acoustic 0.9970
    "excitation": "pick",        # Bright hard attack from plectrum
    "width": 0.6,                # Moderate pulse width (stiffer nylon = brighter)
    "lowpass_hz": 5000,          # Magnetic pickup bandpass — strings have
                                 #   energy to ~8 kHz, pickup rolls off
    "noise_component": 0.025,    # Pick click/scrape on wound strings
}

# ModalSynth fallback
MODAL_PRESET = "string"

# PhaseMod alt (cheap guitar emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",      # Even+odd harmonics for string vibration
    "mod_freq_ratio": 1.0,       # Octave doubling
    "mod_depth": 2.0,            # Moderate FM twang
    "attack": 0.005,             # Fast pick transient
    "release": 0.20,             # Short damping
}

# Production defaults
REVERB_TAIL = 1.8        # seconds, room/spring — clean electric typically
                          # uses amp spring reverb (Fender outboard tank
                          # ~2.0 s decay character)
EQ_BODY = (300, -3.0)    # peaking cut Hz, dB — reduce box resonance
                          # from the solidbody at 200–400 Hz
EQ_PRESENCE = (3500, 2.5) # peaking boost Hz, dB — pick attack, fret
                          # noise, pickup "quack"
EQ_AIR = (8000, 1.5)     # highshelf Hz, dB — gentle string shimmer,
                          # pickup bandwidth ceiling
PAN = -0.2               # centre-left for standard mono stage amp;
                          # stereo double has the other at +0.2


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)