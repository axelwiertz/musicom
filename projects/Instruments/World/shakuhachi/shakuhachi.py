# -*- coding: utf-8 -*-
"""Shakuhachi — musicom instrument constants.

Japanese end-blown bamboo flute (1.8 shaku, ~54.5 cm). GM77.
Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.

Line-instrument quirk: shakuhachi is a monophonic Zen/folk flute (honkyoku
tradition) — the instrument is inherently a single melodic line; no chords.
"""

MIDI_PROGRAM = 77
GM_NAME = "Shakuhachi"
# RenderPipeline stem label: GM_PROGRAMS[77] = "Shakuhachi" (exact match, no quirk)
STEM_LABEL = "Shakuhachi"

# MIDI ranges (1.8-shaku standard bamboo flute; longer flutes go lower)
RANGE_MIN = 55       # G3 (2.4-shaku fundamental)
RANGE_MAX = 100      # E7 (dai-kan, expert only)
SOLO_RANGE = (62, 86)   # D4-D6 standard 2-octave honkyoku core
SWEET_SPOT = (64, 84)   # E4-D6, the expressive melodic zone

# Register zones (Japanese names)
ZONES = {
    "otsu": (62, 73),       # D4-D5, lower register — dark, full, meditative
    "kan": (74, 85),        # E5-D6, upper register — bright, penetrating
    "dai_kan": (86, 100),   # E6-E7, partial 3rd octave — airy, extended
}

# Articulation defaults (velocity, duration_factor)
# Shakuhachi uses oshi (finger-hit) not tonguing; meri/kari for pitch bending
ARTICULATIONS = {
    "legato": (72, 1.0),       # sustained, connected (no tonguing)
    "staccato": (60, 0.30),    # short oshi break
    "muraiki": (88, 0.80),     # explosive breath blast attack
    "meri": (75, 1.0),         # lowered pitch (bend downward)
    "kari": (78, 1.0),         # raised pitch (bend upward)
    "yuri": (70, 1.0),         # horizontal vibrato (pitch modulation)
    "accent": (92, 0.85),      # emphasized tsuyoshi oshi
    "breath": (48, 1.0),       # breathy tone, minimal pitch
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.0,       # bamboo tube resonator
    "mod_depth": 2.0,            # more than flute 1.5 — richer upper harmonics
    "attack": 0.06,              # breath onset (between flute 0.08 and clarinet 0.05)
    "release": 0.20,             # bamboo resonance — longer than flute 0.15
}

# Production defaults
REVERB_TAIL = 2.5       # seconds, long hall — shakuhachi loves Zen temple space
EQ_BODY = (400, -1.5)   # peaking cut Hz, dB — reduce bamboo box resonance
EQ_PRESENCE = (3500, 2.5)  # peaking boost Hz, dB — breathy edgy presence
PAN = 0.0               # center for solo; slightly left in koto ensemble


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)