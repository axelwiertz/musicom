# -*- coding: utf-8 -*-
"""Distortion Guitar — musicom instrument constants.

GM30 = Distortion Guitar. The solidbody electric guitar pushed into hard
tube-amp distortion — the heavy rock/metal lead and rhythm voice. Six
strings, humbucker pickups, high-gain tube amp (Marshall JCM800/5150-style),
4x12 cabinet. The heavier sibling of Overdriven Guitar (GM29): harder
clipping, more compression sustain, tighter palm-muted chug.

Reference range for the standard 22-fret guitar: MIDI 40-76 (E2-E6).
The GM patch (FluidR3 preset 30) spans wider, 28-84 (E1-C6).

Distortion quirk: hard clipping intermodulates chords even more than
overdrive, so idiomatic writing is single-note leads and power chords
(root-fifth, no 3rd) — never dense full-position chords.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 30
GM_NAME = "Distortion Guitar"
# RenderPipeline stem label: GM_PROGRAMS[30] = "Distortion Guitar"
#   -> stem file trackXX_Distortion_Guitar.wav (matches pipeline label;
#   FluidR3 preset 30 = "Distortion Guitar" — labels match exactly, no quirk)
STEM_LABEL = "Distortion_Guitar"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 28       # E1 — GM patch floor (real guitar E2=40)
RANGE_MAX = 84       # C6 — GM patch ceiling (real 22-fret ceiling E6=76)
SOLO_RANGE = (45, 76)   # A2-E6 — idiomatic lead zone: single-note scream
                        #   lines, melodic fills, power-chord riffs
SWEET_SPOT = (52, 72)   # E3-C5 — the distortion pocket: rich harmonic
                        #   saturation, fat leads and chunky chug riffs

# Register zones
ZONES = {
    "low_strings": (28, 47),    # E1-B2 — palm-muted chug roots: the metal
                                #   rhythm engine, low growl, power-chord roots
    "mid": (48, 64),            # C3-E4 — the distortion sweet spot: power-
                                #   chord pocket, riff centre, fat singing leads
    "high": (65, 84),           # F4-C6 — screaming single-note leads,
                                #   harmonics, bridge-pickup squeal territory
}

# Articulation defaults (velocity, duration_factor)
# Distortion guitar articulations — hard clipping compresses dynamics even
# harder than overdrive (~10 dB range). Idiomatic velocities 70-100; the
# expressive levers are pick attack (palm mute vs open) and note density.
ARTICULATIONS = {
    "sustained_lead": (86, 1.0),       # Singing legato line — the default
                                       #   distortion lead articulation
    "power_chord": (90, 0.40),         # Root-fifth power chord — no 3rd, the
                                       #   #1 rhythm technique in rock/metal
    "palm_mute": (58, 0.10),           # Edge-of-hand damped — percussive chug,
                                       #   the metal rhythm foundation
    "open_chord": (78, 0.45),          # Full strumed chord — heavily compressed
    "staccato": (68, 0.12),            # Quick muted chord stab — rhythmic accent
    "bend": (96, 1.30),                # Wide string bend — pitch rise + maximum
                                       #   sustain; the scream-lead signature
    "hammer_on": (80, 0.60),           # Legato slur up — pronounced on gain
    "pull_off": (70, 0.60),            # Legato slur down — connected line
    "slide": (74, 0.90),               # Continuous pitch glide
    "vibrato": (82, 1.0),              # Arm whammy or finger vibrato
    "harmonic": (93, 0.40),            # Natural overtone — sustained by amp
    "grace": (72, 0.10),               # Quick pre-note flick
    "accent": (100, 0.30),             # Emphatic pick dig/hard hit
    "feedback": (66, 1.50),            # Amp–guitar coupling squeal sustain
    "tremolo_pick": (84, 0.25),        # Rapid alternate picking — the metal
                                       #   rhythm signature (16ths at 140+bpm)
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"   # sound/synthesis/karplus_strong.py KSModel
                               # Distortion guitar IS a plucked steel string
                               # with a non-linear distortion stage — the
                               # Karplus-Strong waveguide is the exact
                               # physical model, with HARDER clipping than
                               # the overdriven (GM29) stage
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9992,            # HIGHEST in the plucked set — hard-clip
                                      #   compression extends sustain to
                                      #   10-20+ s (overdriven 0.9990)
    "excitation": "pick",             # Bright hard attack from plectrum
    "width": 0.50,                    # Narrower than overdriven 0.55 —
                                      #   compressed string envelope
    "lowpass_hz": 3800,               # Heavier speaker roll-off than
                                      #   overdriven 4000 — darker, thicker
    "noise_component": 0.080,         # Highest in the guitar family — tube
                                      #   hiss + gain-stage noise floor
    "saturation": 0.85,               # Hard clipping (overdriven 0.60 is
                                      #   soft-knee; distortion is harder)
}

# ModalSynth fallback (weak — modal models miss the saturation character)
MODAL_PRESET = "string"

# PhaseMod alt (FM distortion emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",          # Even+odd harmonics of a string
    "mod_freq_ratio": 1.0,           # Fundamental modulation
    "mod_depth": 4.5,                # HIGHEST FM depth in the Guitar family —
                                     #   harmonic foldover = the distortion
                                     #   scream (overdriven 4.0)
    "attack": 0.005,                 # Fast pick transient
    "release": 0.60,                 # Longer — amp sustain/compression
}

# Additive fallback (harmonic stack approximating the clipped waveform)
ADDITIVE_DEFAULTS = {
    "harmonic_count": 9,
    "harmonic_weights": [0.9, 0.7, 0.85, 0.55, 0.75, 0.45, 0.55, 0.35, 0.3],
    "attack": 0.005,
    "release": 0.60,
}

# Production defaults
REVERB_TAIL = 2.4        # seconds, hall/room — big rock/metal stage; longer
                         #   than overdriven 2.2 (the lead screams in space)
EQ_BODY = (400, -4.5)    # Peaking cut at 400 Hz — reduce box/mud from
                         #   distortion harmonic buildup (heavier than
                         #   overdriven -4.0)
EQ_PRESENCE = (2500, 3.0) # Peaking boost at 2.5 kHz — pick attack + chug
                         #   articulation clarity in the mix
EQ_AIR = (5500, 0.5)     # High shelf at 5.5 kHz — gentle top; the amp
                         #   speaker has already rolled off above ~4 kHz
PAN = -0.15              # Centre-left for mono stage amp; stereo double at +0.15


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
