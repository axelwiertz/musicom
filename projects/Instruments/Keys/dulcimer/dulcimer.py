# -*- coding: utf-8 -*-
"""Dulcimer — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — sound/synthesis/modal.py). A hammered dulcimer is a struck
string over a soundboard: the hard hammer gives a sharp attack transient and
the struck string pair rings with fast-decaying harmonic partials over a
bright wooden body. The ModalSynth 'string' preset (harmonic series,
moderate decay, impulse excitation) is the closest stock match; the custom
dulcimer resonator modes in instrument.md (higher decay rates on the upper
partials = struck-string physics) are the refined patch. Karplus-Strong is
the alternative (plucked-waveguide, loop_gain 0.9975 — long bright ring on
the doubled treble courses). The FM_DEFAULTS below are the cheap alternative.
"""

MIDI_PROGRAM = 15
GM_NAME = "Dulcimer"
# RenderPipeline stem label: GM_PROGRAMS[15] = "Dulcimer" -> stem file
# trackXX_Dulcimer.wav (matches exactly, no quirk; FluidR3 preset 15 =
# "Dulcimer" — hammered-dulcimer sample set with bright struck-string timbre)
STEM_LABEL = "Dulcimer"

# MIDI ranges (sounding pitch; concert hammered dulcimer, 3-octave chromatic
# layout C3-C6 with doubled treble courses; MIDI-keyboard layout extends
# practical register a bit further each way)
RANGE_MIN = 48      # C3 — lowest hammered-dulcimer course (some 4-octave
                    #   instruments extend to G2=43; C3 is the standard floor)
RANGE_MAX = 96      # C7 — practical top (bright, thin above ~A6=93)
SOLO_RANGE = (60, 89)   # C4–A6 — solo repertoire focus (folk/dance tunes)
SWEET_SPOT = (62, 86)   # D4–D6 — fullest body ring + hammer articulation

# Register zones
ZONES = {
    "low": (48, 59),     # C3–B3 — bass courses; dark, long wooden-body ring
    "mid": (60, 77),     # C4–F5 — melody courses (primary register)
    "high": (78, 96),    # F#5–C7 — treble courses; bright, thin, fast decay
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "hammer": (80, 1.0),    # standard hammer stroke — full course ring
    "roll": (70, 0.10),     # tremolo roll (fast alternating hammers)
    "double": (74, 0.25),   # double/triple stroke — rhythmic figure
    "damped": (46, 0.10),   # palm/chord damp — choked dry attack
    "accent": (96, 0.85),   # hard hammer — bright cutting emphasis
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # ModalSynth resonator bank (impulse excitation)
MODAL_PRESET = "string" # harmonic-series plucked-string stock preset;
                        #   custom struck-string modes in instrument.md
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,    # low damping -> long bright ring on doubled
                            #   treble courses (sitar-class sustain)
    "width": 0.45,          # slight stereo spread per note
    "role": "lead",
}

# Phase-mod alternative patch (cheap dulcimer)
FM_DEFAULTS = {
    "carrier_shape": "triangle",
    "mod_freq_ratio": 2.0,
    "mod_depth": 2.0,
    "attack": 0.002,
    "release": 0.35,
}

# Production defaults
REVERB_TAIL = 1.2       # seconds, room/plate — bright folk box; keep
                        #   hammer attack (shorter than koto 1.4 / sitar 2.2)
EQ_BODY = (350, -2.0)   # peaking cut Hz, dB — tame soundboard boxiness
EQ_PRESENCE = (3200, 2.5)  # peaking boost Hz, dB — hammer click + string sparkle
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — subtle air; treble courses bright
PAN = 0.0               # center for solo; +0.2..0.3 spread for accompaniment


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
