# -*- coding: utf-8 -*-
"""Marimba — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 12
GM_NAME = "Marimba"
# RenderPipeline stem label: GM_PROGRAMS[12] = "Marimba" -> stem file
# trackXX_Marimba.wav (matches exactly, no quirk; SF2 preset 12 = "Marimba")
STEM_LABEL = "Marimba"

# MIDI ranges (standard 5-octave marimba, sounding pitch)
RANGE_MIN = 45      # A2 (4.3-octave marimba bottom; 5-octave goes to C2=36)
RANGE_MAX = 96      # C7 (top of 5-octave; 4.3-octave tops at C7=96 too)
SOLO_RANGE = (60, 84)   # C4-C6 — solo repertoire focus
SWEET_SPOT = (60, 84)   # C4-C6 — warm round tone, best projection

# Register zones
ZONES = {
    "low": (45, 59),     # A2-B3, dark woody bass bars, long decay
    "mid": (60, 71),     # C4-B4, warm round singing voice
    "high": (72, 96),    # C5-C7, bright dry cutting, mallet click
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),       # single stroke — mallet strike + natural decay
    "roll": (68, 0.06),         # tremolo — rapid alternating mallets
    "staccato": (64, 0.2),      # short, dry, separated
    "accent": (96, 0.9),        # hard mallet emphasis
    "dead_stroke": (48, 0.15),  # muted/choked bar
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "marimba"

# Production defaults
REVERB_TAIL = 1.0       # seconds, room/plate — keep the mallet attack clear
EQ_BODY = (400, -2.0)   # peaking cut Hz, dB — clear woody boxiness
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — mallet clarity
EQ_AIR = (7000, 1.0)    # highshelf Hz, dB — subtle air, bars already bright
PAN = 0.0               # center for solo; +0.2..0.35 spread for sections


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
