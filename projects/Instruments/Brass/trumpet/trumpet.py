# -*- coding: utf-8 -*-
"""Trumpet — musicom instrument constants."""

MIDI_PROGRAM = 56
GM_NAME = "Trumpet"

RANGE_MIN = 54       # F#3
RANGE_MAX = 86       # D6
SOLO_RANGE = (60, 84)

ZONES = {
    "low": (54, 65),
    "mid": (66, 79),
    "high": (80, 86),
}

ARTICULATIONS = {
    "sustain": (85, 1.0),
    "staccato": (68, 0.25),
    "marcato": (98, 0.9),
    "sforzando": (108, 0.7),
    "muted": (60, 0.8),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.5,
    "mod_depth": 4.0,
    "attack": 0.02,
    "release": 0.1,
}

# Production
REVERB_TAIL = 1.0
EQ_PRESENCE = (4000, 3.0)
PAN = 0.0


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
