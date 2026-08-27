# -*- coding: utf-8 -*-
"""Acoustic Guitar — musicom instrument constants."""

MIDI_PROGRAM = 25
GM_NAME = "Acoustic Guitar (nylon)"

RANGE_MIN = 40       # E2
RANGE_MAX = 84       # C6
SOLO_RANGE = (48, 76)

ZONES = {
    "bass_strings": (40, 47),
    "middle": (48, 59),
    "high": (60, 84),
}

ARTICULATIONS = {
    "strum": (72, 0.25),
    "arpeggio": (65, 0.2),
    "muted": (48, 0.125),
    "hammer_on": (72, 0.5),
}

SYNTHESIS = "modal"
MODAL_PRESET = "string"

# Production
REVERB_TAIL = 0.8
EQ_PRESENCE = (3000, 2.0)
PAN = -0.2


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
