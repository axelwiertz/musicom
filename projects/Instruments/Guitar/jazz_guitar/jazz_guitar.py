# -*- coding: utf-8 -*-
"""Jazz Guitar — musicom instrument constants.

GM 26 = Electric Guitar (jazz). The archtop hollow-body electric guitar — the
jazz guitar (Gibson ES-175 / L-5 / Super 400 lineage). Six strings, f-hole
hollow body, magnetic pickup, THUMB attack (Wes Montgomery). Warm, round,
dark voice: neck-pickup archtop tone with flatwound strings, played with the
fleshy thumb instead of a pick — the roundest, most vocal guitar timbre.

Reference range for the standard 22-fret guitar: MIDI 40–76 (E2–E6).
The GM patch (FluidR3 preset 26) spans wider, 28–84 (E1–C6).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 26
GM_NAME = "Electric Guitar (jazz)"
# RenderPipeline stem label: GM_PROGRAMS[26] = "Electric Guitar (jazz)"
#   -> stem file trackXX_Electric_Guitar_jazz.wav (matches pipeline label;
#   FluidR3 preset 26 = "Jazz Guitar" — the SF2 uses the common name while
#   the pipeline uses the GM2 spec spelling; cosmetic only, no routing
#   impact. STEM_LABEL matches the pipeline's real label so stem-file
#   lookups work.)
STEM_LABEL = "Electric_Guitar_jazz"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 28       # E1 — GM patch floor (real guitar E2=40)
RANGE_MAX = 84       # C6 — GM patch ceiling (real 22-fret ceiling E6=76)
SOLO_RANGE = (43, 76)   # G2–E6 — idiomatic lead zone: single-note lines,
                        #   octave melodies (Wes style), thumb attack
SWEET_SPOT = (48, 72)   # C3–C5 — comping heart: shell voicings, neck-
                        #   pickup warmth, Freddie Green chords

# Register zones
ZONES = {
    "low_strings": (28, 47),    # E1–B2 — low roots, bass-note comping,
                                #   walk-downs; dark thud zone
    "mid": (48, 64),            # C3–E4 — THE jazz zone: comping chords,
                                #   shell voicings, thumb melodies
    "high": (65, 84),           # F4–C6 — octave melodies, single-note
                                #   fills, block-chord top notes
}

# Articulation defaults (velocity, duration_factor)
# Jazz guitar articulations map to thumb/pick/finger techniques
ARTICULATIONS = {
    "thumb": (75, 0.9),        # Fleshy thumb stroke — the Wes Montgomery
                               #   signature: round, warm, no pick click,
                               #   slightly softer attack, full ring
    "pick": (72, 0.35),        # Plectrum — brighter attack, thinner tone,
                               #   jazz-fusion edge (Pat Metheny)
    "finger": (65, 1.0),       # Fingertip pluck — warm, round, mellow
    "comp_chord": (60, 0.25),  # Freddie Green-style rhythm comp — short,
                               #   percussive chord strokes on beats 2 & 4
    "shell_voicing": (55, 0.5),# 3-note shell chord (root-7th-3rd) — light,
                               #   breathable comping, the jazz default
    "octave": (72, 0.6),       # Wes-style doubled octave melody — the
                               #   classic jazz guitar lead texture
    "hammer_on": (72, 0.5),    # Legato slur upward — connecting notes
                               #   without picking, smooth line
    "pull_off": (62, 0.5),     # Legato slur downward — connecting notes
                               #   without picking
    "slide": (70, 0.8),        # Fret slide — continuous pitch glide
    "bend": (80, 0.9),         # String bend — pitch rise, bluesy edge
                               #   (less common in pure jazz, idiomatic in
                               #   jazz-blues)
    "vibrato": (68, 0.9),      # Finger vibrato — the vocal-like sustain
                               #   that IS the jazz guitar lead sound
    "arpeggio": (62, 0.3),     # Fingerpicked rolled chord — fluid texture
    "ghost_note": (42, 0.08),  # Muted scratch — no defined pitch, rhythm
                               #   texture (funk-inflected comping)
    "accent": (92, 0.30),      # Hard dig — cutting chord hit or lead peak
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"  # sound/synthesis/karplus_strong.py KSModel
                              # Jazz guitar IS a plucked string — Karplus-
                              # Strong waveguide is the exact physical
                              # model for the string vibration; the archtop
                              # body + flatwound string + thumb define the
                              # dark, warm damping character.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,         # Flatwound strings ring long & smooth
                                 #   (2–4 s); between steel_acoustic 0.9970
                                 #   and harp 0.9985; overdriven 0.9990 is
                                 #   the compression sustain
    "excitation": "thumb",       # Fleshy thumb — round attack, no pick
                                 #   click transient
    "width": 0.5,                # Moderate pulse width (round, not bright)
    "lowpass_hz": 3500,          # Archtop neck-pickup rolloff — darker than
                                 #   clean electric 5000: flatwounds + f-hole
                                 #   body absorb the highs
    "noise_component": 0.015,    # Low — thumb is quiet, flatwounds reduce
                                 #   finger noise (vs pick scratch 0.025)
}

# ModalSynth fallback
MODAL_PRESET = "string"

# PhaseMod alt (cheap guitar emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",      # Even+odd harmonics for string vibration
    "mod_freq_ratio": 1.0,       # Octave doubling
    "mod_depth": 1.5,            # Gentle FM twang — jazz tone is NOT
                                 #   brassy; keep the modulation shallow
    "attack": 0.01,              # Fast thumb transient
    "release": 0.25,             # Moderate damping
}

# Production defaults
REVERB_TAIL = 2.0        # seconds, jazz-club room / warm hall — the jazz
                          # guitar lives in a small-room ambience with
                          # plate reverb on ballads (Wes: dry amp + room;
                          # Joe Pass: hall)
EQ_BODY = (250, -2.0)    # peaking cut Hz, dB — reduce archtop boxiness/
                          # boominess from the hollow body at 200–300 Hz
EQ_PRESENCE = (2800, 2.0) # peaking boost Hz, dB — neck-pickup warmth,
                          # thumb-attack definition without harshness
EQ_AIR = (7500, 1.0)     # highshelf Hz, dB — gentle air only: the jazz
                          # tone is DARK by design (vs clean electric
                          # 8 kHz +1.5)
PAN = -0.2               # centre-left for standard guitar seating (amp on
                          # stage left of the drummer); stereo double at
                          # +0.2


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
