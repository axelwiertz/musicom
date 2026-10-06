# -*- coding: utf-8 -*-
"""Rhodes (Electric Piano 1) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (struck metal-bar
modes — sound/synthesis/modal.py). The Rhodes tine is a struck clamped-
cantilever steel reed with a spring-coil base; its partials are inharmonic
and compressed. A custom RHODES_MODES bank at compressed ratios models the
"bell" character accurately.

Identity: GM4 = Electric Piano 1 (Fender Rhodes / Wurlitzer electromechanical
piano). A fully polyphonic keyboard — melody, harmony, and bass all at once.
Pickup compression narrows the dynamic range vs an acoustic piano; phrase
with voicing density as much as with velocity.
"""

MIDI_PROGRAM = 4
GM_NAME = "Electric Piano 1"
# RenderPipeline stem label: GM_PROGRAMS[4] = "Electric Piano 1" -> stem file
# trackXX_Electric_Piano_1.wav (matches exactly, no quirk; FluidR3 preset 4 =
# "Electric Piano 1", phdr-verified)
STEM_LABEL = "Electric_Piano_1"

# MIDI ranges (73-note Rhodes Mark I: E2-E6 = 40-88; extended 88-key to C8)
RANGE_MIN = 36      # E1 — lowest note on 73/88-key compass
RANGE_MAX = 96      # C7 — GM patch span (88-key spans 21-108, we cap at
                    #   C7 for practical audibility)
SOLO_RANGE = (48, 84)   # C3–C6 — primary melodic + harmonic register
SWEET_SPOT = (60, 79)   # C4–G5 — bell-like "bark" zone, the classic Rhodes
                        #   solo register

# Register zones
ZONES = {
    "low": (36, 47),     # E1–B2 — bass zone: dark, rumbly, soft fundamental
    "mid_low": (48, 59),  # C3–B3 — lower mid: warm bell, chord comping
    "mid": (60, 79),      # C4–G5 — primary bell register, the "bark" zone
                          #   (accented notes at velocity ≥95 growl here)
    "high": (80, 96),     # G#5–C7 — bright tinkly top, compressed sparkle
}

# Articulation defaults (velocity, duration_factor).
# NOTE: pickup compression narrows the dynamic range — a "hard accent" at 112
# is only ~3-4 dB louder than a "touch" at 72 in the RMS, unlike a piano where
# the difference would be ~15-20 dB. Use REGISTRATION (voicing density, chord
# spacing) for dynamic contour as much as velocity.
ARTICULATIONS = {
    "legato_pedal": (50, 1.0),       # soft pedal, full ring — the "water"
    "touch": (70, 1.0),              # neutral finger, chord comping
    "accent": (92, 0.95),            # mid-velocity bark zone attack
    "hard_accent": (108, 0.95),      # high velocity, pickup saturation + snarl
    "staccato": (75, 0.25),          # damped short, funk/pop chop
    "bark": (100, 0.9),              # the iconic Rhodes "bite" at C4-C5
    "tremolo": (60, 1.0),            # sustained with amp tremolo (5.5 Hz AM)
    "muted_tine": (38, 0.20),        # felt-muted, barely rings — delicate
    "comping_chop": (78, 0.50),      # rhythmic chord stab for pop/funk
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # sound/synthesis/modal.py — ModalSynth
MODAL_PRESET = "string"  # closest stock bank (harmonic stack, moderate decay)
                        #   — the "clean struck metal" fallback

# Modal custom bank for the mid-register tine (A4 reference). The Rhodes tine
# has compressed inharmonic partials (the spring-coil base pushes modes
# down from harmonic). Decay rates are moderate — tine ring 0.5-2 s bright,
# 2-6 s total tail.
RHODES_MODES = [
    (440.0, 1.00, 1.5),    # f0 (A4) — tine fundamental, 1.5 decay rate
    (1012.0, 0.55, 1.8),   # 2.3x — first overtone, the "bell" octave+2nd
    (1804.0, 0.20, 2.2),   # 4.1x — compressed 4th mode, attack edge
    (2992.0, 0.08, 3.0),   # 6.8x — high clank, fast decaying (hammer tick)
]

# Karplus-Strong: the tine IS a struck waveguide (clamped steel reed).
# loop_gain 0.9965 — between clavi 0.9960 (rubber-mute damped) and sitar
# 0.9975 (long sympathetic ring). Steel tine rings 1-3 s, damped by felt
# on key release. Low-pass feedback for the pickup's limited high response.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9965,    # between clavi (short) and sitar (long)
    "width": 0.7,           # stereo width — piano keyboard spread
    "role": "rhodes",       # tags for synthesis routing
    "lowpass_hz": 2000,     # pickup bandwidth — reduced highs vs pure string
    "noise_component": 0.015,  # hammer felt tick transient
}

# PhaseModSynth (FM) alternative — bell-like FM piano
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.3,  # 2.3x — the "bell" partial (2x = octave, but
                             #   Rhodes tine is slightly stretched inharmonic)
    "mod_depth": 1.8,       # moderate — Rhodes is less nasal than harpsichord
                             #   (2.2) and less buzzy than a reed (3.0+)
    "attack": 0.004,         # felt hammer on steel — fast but not instant
    "release": 1.5,          # tine ring continues after key lifts (dampers
                             #   are felt rests, slower than quill or hammer)
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, hall — the "watery" chord wash IS the
                        #   Rhodes sound; hall reverb with 50-80 ms pre-delay
                        #   keeps the attack definition (shorter tail when
                        #   used as a pop comping pad, 1.2-1.5 s)
EQ_BODY = (350, -2.5)   # peaking cut Hz, dB — tame tine-mount body resonance
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — bell articulation + pickup
                           #   clarity; the "bark" zone lives around 1.5-3 kHz
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — subtle air; pickup noise lives
                        #   at 6-10 kHz, don't boost too much
PAN = 0.0               # center for solo; classical stereo: Rhodes panned
                        #   slightly left (audience view, keyboard centre-right
                        #   in a stage mix)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)