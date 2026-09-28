# -*- coding: utf-8 -*-
"""Pan Flute — musicom instrument constants.

South American Andean panpipes (zampoña / siku / antara). GM75.
Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Line-instrument quirk: pan flute is a monophonic breath line — each tube
produces one pitch; NO dense chords. The siku tradition uses complementary
arqa/ira pairs for rapid alternation but the instrument is inherently a
single melodic line.
"""

MIDI_PROGRAM = 75
GM_NAME = "Pan Flute"
# RenderPipeline stem label: GM_PROGRAMS[75] = "Pan Flute" (exact match)
# -> trackXX_Pan_Flute.wav (no quirk; FluidR3 preset 75 = "Pan Flute")
STEM_LABEL = "Pan_Flute"

# MIDI ranges (large chromatic zampoña set, sounding pitch)
RANGE_MIN = 55       # G3 — bass zankha tube, large 3-octave sets
RANGE_MAX = 100      # E7 — chuli high register, smallest tubes
SOLO_RANGE = (62, 89)   # D4–F6 — standard siku/zampoña solo repertoire
SWEET_SPOT = (64, 84)   # E4–C6 — malta mid register, warmest round tone

# Register zones (Aymara names: zankha / malta / chuli)
ZONES = {
    "zankha": (55, 61),    # G3–B3, bass tubes — deep, airy, breathy
    "malta": (62, 78),     # D4–F5, middle tubes — primary melodic register
    "chuli": (79, 100),    # F#5–E7, high tubes — bright, piercing, whistle-like
}

# Articulation defaults (velocity, duration_factor)
# Pan flute uses breath + tongue stops; no keys or reeds
ARTICULATIONS = {
    "sustain": (78, 1.0),      # sustained breath, gentle blow
    "staccato": (65, 0.30),   # short breath cutoff, tongue stop
    "accent": (90, 0.85),     # emphatic blow — breathy burst, slight pitch bend up
    "legato": (72, 1.0),      # smooth breath transitions between tubes
    "trill": (70, 0.20),      # fast alternation between adjacent tubes
    "grace": (62, 0.15),      # quick breath pulse before main note
    "vibrato": (75, 1.0),     # jaw vibrato — characteristic Andean quaver
    "airy": (50, 1.0),        # soft, breathy tone — half-pitch harmonics
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.0,       # stopped-pipe resonator (fundamental only)
    "mod_depth": 1.2,            # shallow — pure fundamental dominant, odd partials weak
    "attack": 0.05,              # gentle breath onset (between flute 0.08 and ocarina 0.06)
    "release": 0.15,             # natural breath cutoff (same as flute 0.15)
}

# Additive synthesis fallback (odd-only partials — stopped pipe)
ADDITIVE_DEFAULTS = {
    "partials": [(1, 0.9), (3, 0.35), (5, 0.15), (7, 0.05)],
    "attack": 0.05,
    "release": 0.15,
}

# AirPipe physical model fallback
AIRPIPE_DEFAULTS = {
    "stopped": True,
    "length_scale": 0.85,
    "pressure": 0.55,
    "noise": 0.15,
}

# Production defaults
REVERB_TAIL = 2.0       # seconds, hall — mountain-valley space
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — reduce tube resonance boxiness
EQ_PRESENCE = (2200, 2.0)  # peaking boost Hz, dB — breath presence + warmth
EQ_AIR = (8000, 0.0)    # natural roll-off above 8 kHz (stopped-pipe cut)
PAN = 0.0               # center for solo; ±0.15 for arqa/ira stereo pair


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)