# -*- coding: utf-8 -*-
"""Brass Section — musicom instrument constants.

GM 61 = Brass Section. The full brass ensemble patch: trumpets, trombones,
french horns, tuba playing together in a single multi-sample patch.

Reference: the GM patch spans MIDI 36-96 (C2-C7). The idiomatic brass section
register is C3-C6 (48-84) — the richest tutti blend.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 61
GM_NAME = "Brass Section"
# RenderPipeline stem label: GM_PROGRAMS[61] = "Brass Section"
#   -> stem file trackXX_Brass_Section.wav (matches pipeline label;
#   FluidR3 preset 61 = "Brass Section" — same label, no quirk)
STEM_LABEL = "Brass_Section"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 36       # C2 — GM patch floor
RANGE_MAX = 96       # C7 — GM patch ceiling
SOLO_RANGE = (48, 84)   # C3-C6 — idiomatic tutti brass zone
SWEET_SPOT = (55, 79)   # G3-G5 — richest ensemble blend

# Register zones
ZONES = {
    "low": (36, 55),          # C2-G3 — ensemble bass: trombones + tuba
    "mid": (56, 71),          # B3-C5 — the horn call zone: fanfares, sustained
    "high": (72, 84),         # C5-C6 — trumpet-dominant lead: piercing top line
    "top_extension": (85, 96), # C6-C7 — thin ensemble scream
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (82, 1.0),
    "fanfare_stab": (92, 0.40),
    "marcato": (85, 0.65),
    "accent": (98, 0.30),
    "staccato": (70, 0.20),
    "sfz": (100, 0.25),
    "swell": (72, 1.20),
    "sfp": (65, 1.10),
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth
                           # Brass section is sustained multi-brass ensemble

FM_DEFAULTS = {
    "carrier_shape": "saw",       # Rich harmonics for brass ensemble
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,        # Fundamental emphasis
    "mod_depth": 2.8,             # Between french_horn (2.5) and muted_trumpet (3.5)
    "attack": 0.06,               # Ensemble attack
    "release": 0.30,              # Medium release for brass resonance
}

# Additive fallback
ADDITIVE_DEFAULTS = {
    "harmonic_count": 8,
    "harmonic_weights": [1.0, 0.85, 0.65, 0.50, 0.35, 0.20, 0.12, 0.08],
    "attack": 0.06,
    "release": 0.30,
}

# ModalSynth fallback (weak — misses brass harmonic saturation)
MODAL_PRESET = "string"

# Production defaults
REVERB_TAIL = 2.5        # seconds, concert hall — brass needs more tail
EQ_BODY = (250, -3.0)    # Peaking cut at 250 Hz — reduce low-mid mud
EQ_PRESENCE = (2500, 3.5) # Peaking boost at 2.5 kHz — brass edge and projection
EQ_AIR = (8000, 1.0)     # High shelf at 8 kHz — open the ensemble
PAN = -0.25              # Centre-left (brass sits stage-left in orchestra)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)