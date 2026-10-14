# -*- coding: utf-8 -*-
"""Overdriven Guitar — musicom instrument constants.

GM 29 = Overdriven Guitar. The solidbody electric guitar pushed into tube amp
saturation — the classic rock lead/rhythm voice. Six strings, humbucker pickups,
Marshall/Vox-style tube amp, 4x12 cabinet.

Reference range for the standard 22-fret guitar: MIDI 40-76 (E2-E6).
The GM patch (FluidR3 preset 29) spans wider, 28-84 (E1-C6).

Overdrive quirk: the distortion compresses and intermodulates chords, so
idiomatic writing uses single-note leads and power chords (root-fifth, no 3rd)
rather than dense full-position chords.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 29
GM_NAME = "Overdriven Guitar"
# RenderPipeline stem label: GM_PROGRAMS[29] = "Overdriven Guitar"
#   -> stem file trackXX_Overdriven_Guitar.wav (matches pipeline label;
#   FluidR3 preset 29 = "Overdrive Guitar" — cosmetic SF2 name difference,
#   no routing impact)
STEM_LABEL = "Overdriven_Guitar"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 28       # E1 — GM patch floor (real guitar E2=40)
RANGE_MAX = 84       # C6 — GM patch ceiling (real 22-fret ceiling E6=76)
SOLO_RANGE = (45, 76)   # A2-E6 — idiomatic lead zone: single-note lines,
                         #   melodic fills, power-chord riffs
SWEET_SPOT = (52, 72)   # E3-C5 — rich harmonic saturation, best projection
                         #   for leads and chunky rhythm riffs

# Register zones
ZONES = {
    "low_strings": (28, 47),    # E1-B2 — bass/fundamental zone: palm-muted
                                #   chugs, low power-chord roots
    "mid": (48, 64),            # C3-E4 — the overdrive sweet spot: rich harmonic
                                #   saturation, fat singing leads
    "high": (65, 84),           # F4-C6 — bright, cutting single-note leads,
                                #   harmonic-rich bridge pickup territory
}

# Articulation defaults (velocity, duration_factor)
# Overdriven guitar articulations — overdrive compression smooths out velocity
# differences compared to clean electric. Idiomatic velocities 70-100.
ARTICULATIONS = {
    "sustained_lead": (82, 1.0),       # Singing legato line — the default
                                       #   overdrive articulation
    "power_chord": (88, 0.40),         # Root-fifth power chord — no 3rd, the #1
                                       #   rhythm technique in rock/punk/metal
    "palm_mute": (55, 0.12),           # Edge-of-hand damped — percussive chug
    "open_chord": (75, 0.45),          # Full strumed chord — compressed by drive
    "staccato": (65, 0.15),            # Quick muted chord stab — rhythmic accent
    "bend": (95, 1.20),                # String bend — pitch rise + maximum sustain
    "hammer_on": (78, 0.60),           # Legato slur up — pronounced on overdrive
    "pull_off": (68, 0.60),            # Legato slur down — connected line
    "slide": (72, 0.90),               # Continuous pitch glide
    "vibrato": (80, 1.0),              # Arm whammy or finger vibrato
    "harmonic": (92, 0.40),            # Natural overtone — sustained by amp
    "grace": (70, 0.10),               # Quick pre-note flick
    "accent": (98, 0.35),              # Emphatic pick dig/hard hit
    "feedback": (65, 1.50),            # Sustained note from amp guitar coupling
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"   # sound/synthesis/karplus_strong.py KSModel
                               # Overdriven guitar IS a plucked steel string with a
                               # non-linear distortion stage — Karplus-Strong waveguide
                               # is the exact physical model
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9990,            # Highest in the plucked set — overdrive
                                      #   compression extends sustain to ~10 s
    "excitation": "pick",             # Bright hard attack from plectrum
    "width": 0.55,                    # Slightly narrower than clean 0.60 — compressed envelope
    "lowpass_hz": 4000,               # Amp speaker roll-off is lower — 4 kHz warm singing tone
    "noise_component": 0.060,         # 2.4x the clean guitar's noise — tube hiss amp floor
    "saturation": 0.60,               # Non-linear waveshaping: soft-knee clipping
}

# ModalSynth fallback (weak — modal models miss the saturation character)
MODAL_PRESET = "string"

# PhaseMod alt (cheap overdrive emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",          # Even+odd harmonics of a string
    "mod_freq_ratio": 1.0,           # Octave doubling
    "mod_depth": 4.0,                # High modulation depth creates harmonic saturation
    "attack": 0.005,                 # Fast pick transient
    "release": 0.50,                 # Longer — amp sustain/compression
}

# Additive fallback (harmonic stack approximating clipped waveform)
ADDITIVE_DEFAULTS = {
    "harmonic_count": 8,
    "harmonic_weights": [0.9, 0.6, 0.8, 0.5, 0.7, 0.4, 0.5, 0.3],
    "attack": 0.005,
    "release": 0.50,
}

# Production defaults
REVERB_TAIL = 2.2        # seconds, hall/room — overdrive typically hybrid spring+room
EQ_BODY = (400, -4.0)    # Peaking cut at 400 Hz — reduce box/mud from overdrive compression
EQ_PRESENCE = (2200, 3.0) # Peaking boost at 2.2 kHz — cutting edge presence
EQ_AIR = (6000, 0.5)     # High shelf at 6 kHz — gentle top, not shrill
PAN = -0.15              # Centre-left for mono stage amp; stereo double at +0.15


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)