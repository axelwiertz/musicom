# -*- coding: utf-8 -*-
"""Blown Bottle — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the blown bottle is a Helmholtz-resonator aerophone — an
air jet across the bottle mouth excites the cavity resonance (the same
physics family as the ocarina, but a WIDE mouth = far more breath
turbulence and a slower, swelly onset). PhaseModSynth is the primary
recommendation (sine carrier + sine modulator at depth 0.7 — the shallowest
of the flute set, reflecting the near-sinusoidal Helmholtz tone — with a
slow 0.12 s attack for the blow-in swell and 0.20 s breath release).
Additive is the fallback (strong fundamental + weak upper partials).
ModalSynth 'bell'/'string' is a struck-resonator alt for short "bloop"
puffs only (the bottle is blown, not struck — KS rejected: no string).

Identity: GM76 = the sound of blowing across the top of an empty bottle
(Helmholtz resonator: pitch set by cavity volume + neck geometry — a
typical soda bottle sits ~100-300 Hz = G2-E4; the GM patch transposes
chromatically). Slow breathy swell notes, near-pure tone, novelty/color
voice. Monophonic breath line — no chords.
"""

MIDI_PROGRAM = 76
GM_NAME = "Blown Bottle"
# RenderPipeline stem label: GM_PROGRAMS[76] = "Blown Bottle" -> stem file
# trackXX_Blown_Bottle.wav (matches exactly, no quirk; FluidR3 preset 76 =
# "Bottle Chiff" — cosmetic SF2 spelling, no routing impact)
STEM_LABEL = "Blown_Bottle"

# MIDI ranges (FluidR3 patch, empirical sweep 24-108 all audible; writing
# band trimmed to where the tone is usable)
RANGE_MIN = 48      # C3 — below this the blow-in swell exceeds ~2 s and the
                    # sub-octave layer dominates (patch plays but unusably slow)
RANGE_MAX = 96      # C7 — above this the patch is increasingly breathy/noisy
                    # (4-8 kHz band ~16% of energy at 84+)
SOLO_RANGE = (60, 84)   # C4–C6 — attack <= ~1 s, pitch identity cleanest
SWEET_SPOT = (65, 79)   # G4–G5 — cleanest Helmholtz tone, moderate breath

# Register zones
ZONES = {
    "low": (48, 59),     # C3–B3 — deep, slow swell (0.5-2 s attack), sub-octave
                         # layer heavy; roots/drone color only, write sparingly
    "mid": (60, 71),     # C4–B4 — primary melody zone, attack <= ~1 s
    "high": (72, 96),    # C5–C7 — fast attack (40-500 ms), breathy sparkle;
                         # 84+ (C6+) gets noisy — accents only
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "blow": (78, 1.0),      # steady sustained blow, full note
    "swell": (85, 1.0),     # long swelling blow — the idiomatic gesture
    "puff": (64, 0.25),     # short re-blown puff (reads as a blip — the slow
                            # attack smears anything shorter than ~1/8)
    "breath": (50, 0.9),    # very airy, half-blown — near-silent colour
    "accent": (95, 0.8),    # hard blow — louder, still swells
    "ghost": (36, 0.15),    # breath click, no real pitch
    "flutter": (70, 0.5),   # rapid re-tongued re-blows (re-articulate, the
                            # patch has no tongue)
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"  # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",          # Helmholtz resonance = near-sine cavity tone
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,            # single dominant resonance
    "mod_depth": 0.7,                 # shallowest of the flute set (ocarina 0.8,
                                      # whistle 1.5) — the bottle is the purest tone
    "attack": 0.12,                   # slow blow-in swell (ocarina 0.06, flute 0.08)
    "release": 0.20,                  # breath tail (same as shakuhachi 0.20)
}
ADDITIVE_DEFAULTS = {
    "harmonic_count": 4,              # Helmholtz resonator suppresses harmonics
    "harmonic_weights": [0.9, 0.25, 0.1, 0.04],  # strong fundamental, weak top
    "attack": 0.12,
    "release": 0.20,
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, small room — nature/folk colour (pan flute
                        # 2.0 / whistle 1.6 / ocarina 1.6)
EQ_BODY = (350, -2.5)   # peaking cut Hz, dB — the patch's sub-octave layer
                        # piles low energy; cut deeper than whistle's 500 Hz
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — breath edge / blow presence
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — gentle breath sparkle (84+ is
                        # already noisy — do NOT push 8 kHz+)
PAN = 0.0               # center for solo; ±0.3 for stereo bottle pairs


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
