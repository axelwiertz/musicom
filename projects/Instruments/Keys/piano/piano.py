# -*- coding: utf-8 -*-
"""Piano — musicom instrument constants."""

MIDI_PROGRAM = 1
GM_NAME = "Acoustic Grand Piano"

RANGE_MIN = 21       # A0
RANGE_MAX = 108      # C8
SOLO_RANGE = (36, 96)

ZONES = {
    "bass": (21, 47),
    "mid": (48, 71),
    "high": (72, 108),
}

ARTICULATIONS = {
    "legato": (72, 1.0),
    "staccato": (65, 0.25),
    "marcato": (95, 0.9),
    "forte": (100, 1.0),
    "piano": (50, 1.0),
    "tremolo": (70, 0.06),
}

SYNTHESIS = "modal"     # ModalSynth custom inharmonic bank
MODAL_PRESET = "marimba"

# Production
REVERB_TAIL = 1.5
EQ_PRESENCE = (3500, 2.0)   # peaking Hz, dB
PAN = 0.0


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
