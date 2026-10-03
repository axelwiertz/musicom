# -*- coding: utf-8 -*-
"""Muted Trumpet — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

GM59 = Muted Trumpet (harmon-muted trumpet — the GM standard specification).
The muted trumpet is a trumpet with a mute inserted in the bell. The GM
default is the harmon (wah-wah) mute, but the instrument covers all common
orchestral/jazz muting: straight, cup, harmon, bucket, plunger.

Synthesis note: the primary recommendation is PhaseModSynth (FM brass,
sound/synthesis/phase_mod.py). The muted tone requires a LOWER mod_depth
(less brassy, more focused) and a SHORTER reverb tail (intimate, not hall).
"""

MIDI_PROGRAM = 59
GM_NAME = "Muted Trumpet"
# RenderPipeline stem label: GM_PROGRAMS[59] = "Muted Trumpet" -> stem file
# trackXX_Muted_Trumpet.wav (matches exactly; FluidR3 preset 59 = "Muted Trumpet")
STEM_LABEL = "Muted Trumpet"

# MIDI ranges (sounding pitch; same physical range as trumpet, muted affects
# timbre not pitch range)
RANGE_MIN = 54      # F#3 — lowest playable (pedal F# to F#3)
RANGE_MAX = 86      # D6 — practical ceiling (solo extension to E6=88)
SOLO_RANGE = (60, 84)   # C4–C6 — solo repertoire focus
SWEET_SPOT = (62, 79)   # D4–G5 — primary melodic register, clearest muted tone

# Register zones
ZONES = {
    "low": (54, 65),     # F#3–F4 — dark, breathy, less projection with mute
    "mid": (66, 79),     # F#4–G5 — primary muted register, focused, nasal
    "high": (80, 86),    # G#5–D6 — bright, thin, cutting (mute brightens in altissimo)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (78, 1.0),      # straight mute — standard, even tone
    "staccato": (64, 0.3),     # crisp articulation — cup mute jazz stabs
    "marcato": (92, 0.9),      # accented, full duration — harmon wah attack
    "cup": (66, 0.9),          # dark, mellow, soft — cup mute ballad tone
    "harmon": (80, 1.0),       # harmon mute, stem in/out — wah-wah capabilty
    "plunger": (85, 0.6),      # plunger mute — talking/wah effect, rhythmic
    "bucket": (60, 0.95),      # bucket mute — very dark, soft, velvety
    "flutter": (72, 1.0),      # flutter-tongue — tremolo effect through mute
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # rich harmonics — brass bore
    "mod_freq_ratio": 2.0,      # 2:1 FM — higher ratio than trumpet (1.5);
                                # produces nasal, focused muted timbre
    "mod_depth": 2.5,           # lower than trumpet (4.0) — less brassy edge,
                                # more focused/nasal muted tone
    "attack": 0.03,             # slightly slower than open trumpet (0.02)
                                # due to mute back-pressure
    "release": 0.12,
}

# Production defaults
REVERB_TAIL = 1.2       # seconds, room — muted trumpet is intimate;
                        # shorter than trumpet (1.8) — no big hall
EQ_BODY = (400, -3.0)   # peaking cut Hz, dB — remove honk/boxiness from mute
EQ_PRESENCE = (3200, 2.5)  # peaking boost Hz, dB — mute buzz + air clarity
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — harmon mute sizzle
PAN = 0.0               # center for solo; -0.1..-0.25 for 2nd part


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)