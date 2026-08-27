# -*- coding: utf-8 -*-
"""Double Bass — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 43
GM_NAME = "Double Bass"     # pipeline labels GM43 "Contrabass"; SF2 preset "Contrabass"

# MIDI ranges
RANGE_MIN = 28      # E1 (4-string, low E; 5-string C1=24)
RANGE_MAX = 74      # D5 (solo extension; orchestral tops ~A4 69)
SOLO_RANGE = (40, 62)   # E2-D4 solo repertoire focus
SWEET_SPOT = (40, 55)   # E2-G3 foundation register, most characteristic

# Register zones
ZONES = {
    "low": (28, 39),
    "mid": (40, 52),
    "high": (53, 74),
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (76, 1.0),
    "pizzicato": (62, 0.2),
    "staccato": (64, 0.25),
    "spiccato": (58, 0.125),
    "tremolo": (68, 0.06),
    "accent": (88, 0.9),
}

# Synthesis engine recommendation
SYNTHESIS = "bowed"     # sound/synthesis/bowed.py BowedString
MODAL_PRESET = "string" # pizzicato via ModalSynth

# Production defaults
REVERB_TAIL = 1.8       # seconds, hall — shorter than cello; keep bass definition
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — clear mud/boxiness
EQ_PRESENCE = (1500, 2.0)  # peaking boost Hz, dB — string attack/wood
PAN = 0.0               # center for solo; -0.2..-0.3 in section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
