# -*- coding: utf-8 -*-
"""Alto Saxophone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 65
GM_NAME = "Alto Saxophone"
# RenderPipeline stem label: GM_PROGRAMS[65] = "Alto Sax" -> stem file is
# trackXX_Alto_Sax.wav (label is "Alto_Sax", NOT "Saxophone" — match on this)
STEM_LABEL = "Alto_Sax"

# MIDI ranges (sounding/concert pitch, Eb alto sax)
RANGE_MIN = 49      # Db3 (concert; written Bb3)
RANGE_MAX = 88      # E6 (practical top incl. altissimo)
SOLO_RANGE = (54, 82)   # F#3-A5 practical solo range
SWEET_SPOT = (61, 79)   # C4-G5 singing solo register, round full tone

# Register zones
ZONES = {
    "low": (49, 60),     # Db3-C4, dark husky breathy, fat but less projection
    "mid": (61, 70),     # C4-B4, warm vocal "vocal fry" edge — ballad territory
    "high": (71, 88),    # C5-E6, bright cutting altissimo scream
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "legato": (80, 1.0),
    "tenuto": (72, 0.9),
    "staccato": (66, 0.25),
    "accent": (92, 0.9),
    "growl": (76, 1.0),      # reed growl/overblow, dirty blues/rock
    "vibrato": (78, 1.0),    # wide deliberate vibrato — sax hallmark
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"     # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical bore single reed: even+odd harmonics
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 2.8,           # brighter/reedier than clarinet (2.0), sax honk
    "attack": 0.04,             # breathy reed onset (20-60 ms)
    "release": 0.10,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, hall — shorter than strings, keep articulation
EQ_BODY = (400, -2.0)   # peaking cut Hz, dB — clear honk/boxiness
EQ_PRESENCE = (2000, 2.5)  # peaking boost Hz, dB — reed core presence
EQ_AIR = (6000, 1.5)    # highshelf Hz, dB — breathy air, subtle
PAN = 0.0               # center for solo lead; +0.2..0.35 in horn section


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
