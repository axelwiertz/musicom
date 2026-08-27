# -*- coding: utf-8 -*-
"""Flute — musicom instrument constants."""

MIDI_PROGRAM = 74
GM_NAME = "Flute"
# RenderPipeline stem label quirk: GM74 is labeled "Recorder" in the
# GM_PROGRAMS list used by sound/render/pipeline.py
STEM_LABEL = "Recorder"

RANGE_MIN = 60       # C4
RANGE_MAX = 96       # C7
SOLO_RANGE = (67, 91)

ZONES = {
    "low": (60, 66),
    "mid": (67, 83),
    "high": (84, 96),
}

ARTICULATIONS = {
    "legato": (75, 1.0),
    "staccato": (62, 0.25),
    "flutter": (68, 1.0),
    "breath": (48, 1.0),
    "accent": (92, 0.9),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.5,
    "attack": 0.08,
    "release": 0.15,
}

# Production
REVERB_TAIL = 2.0
EQ_AIR = (8000, 2.5)
PAN = 0.0


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
