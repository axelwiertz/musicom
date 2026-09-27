# -*- coding: utf-8 -*-
"""Ocarina — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the ocarina is a vessel flute (globular closed chamber with
fipple mouthpiece), not a tube flute. Its physics produce a near-sinusoidal
fundamental with weak upper harmonics (the chamber suppresses overblowing).
PhaseModSynth is the primary recommendation: sine carrier + sine modulator at
a low depth captures the pure vessel-flute tone. Additive (strong fundamental,
rapidly falling harmonic ladder) is an alternative.
"""

MIDI_PROGRAM = 79
GM_NAME = "Ocarina"
# RenderPipeline stem label: GM_PROGRAMS[79] = "Ocarina" -> stem file
# trackXX_Ocarina.wav (matches exactly, no quirk; FluidR3 preset 79 = "Ocarina")
STEM_LABEL = "Ocarina"

# MIDI ranges (sounding pitch, modern 10-hole transverse ocarina)
RANGE_MIN = 55      # G3 — bottom of typical soprano/tenor ocarina
RANGE_MAX = 96      # C7 — top of practical range (bass ocarinas go lower)
SOLO_RANGE = (64, 88)   # E4–E6 — solo repertoire focus
SWEET_SPOT = (72, 84)   # C5–C6 — fullest, clearest tone, most projection

# Register zones
ZONES = {
    "low": (55, 67),     # G3–G4, breathy, soft, darker chamber tone
    "mid": (68, 79),     # G#4–G5, sweetest, clearest, primary singable register
    "high": (80, 96),    # G#5–C7, brighter, thinner, more airy/blowing effort
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (78, 1.0),     # smooth connected breath, natural vessel flute
    "staccato": (62, 0.20),  # tongue-stop, fast cut — clay chamber cuts clean
    "accent": (92, 0.85),    # sharp tongue puff, brighter attack
    "breath": (55, 0.9),     # soft low-velocity, breathy tone
    "trill": (72, 0.35),     # finger trill — fast pitch oscillation
    "portamento": (70, 1.2), # breath-slurred glide across partials
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"  # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",      # vessel flute = nearly pure sine fundamental
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,        # fundamental locked, chamber suppresses overblow
    "mod_depth": 0.8,             # shallow — ocarina has very weak upper harmonics
    "attack": 0.06,               # chamber fills gradually (40-80 ms)
    "release": 0.12,
}
ADDITIVE_DEFAULTS = {
    "harmonic_count": 4,          # only 3-4 harmonics are audible
    "harmonic_weights": [0.9, 0.3, 0.1, 0.03],  # strong fundamental, rapid falloff
    "attack": 0.06,
    "release": 0.15,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, chamber — modest tail, ocarina is intimate
EQ_BODY = (500, -1.5)   # peaking cut Hz, dB — tame clay chamber mid-boxiness
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — fipple breath clarity
EQ_AIR = (8000, 1.8)    # highshelf Hz, dB — gentle breath shimmer, not shrill
PAN = 0.0               # center for solo; ±0.1–0.15 in ensemble


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)