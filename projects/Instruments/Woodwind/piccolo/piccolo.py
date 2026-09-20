# -*- coding: utf-8 -*-
"""Piccolo — musicom instrument constants."""

MIDI_PROGRAM = 72
GM_NAME = "Piccolo"
STEM_LABEL = "Piccolo"

# Sounding range: D5 (74) to C8 (108).
# In notation written one octave lower D4 (62) to C7 (96).
# MIDI here represents sounding pitches (standard GM concert pitch convention).
# Patch also audibly responds down to C5 (72).
RANGE_MIN = 72       # C5 (lowest sounding playable/GM patch limit; standard acoustic bottom is D5=74)
RANGE_MAX = 108      # C8 (highest standard orchestral note)
SOLO_RANGE = (79, 101)  # G5 to F7
SWEET_SPOT = (84, 96)   # C6 to C7 (singing, brilliant high register without extreme shrieking)

ZONES = {
    "low": (72, 79),     # C5–G5 (soft, breathy, quiet, easily covered by orchestra)
    "mid": (80, 91),     # Ab5–G6 (sweet, lyrical, clear, melodic)
    "high": (92, 101),   # Ab6–F7 (brilliant, piercing, cuts through full tutti)
    "altissimo": (102, 108), # F#7–C8 (screaming, shrill, extreme military/climactic fanfare)
}

ARTICULATIONS = {
    "legato": (70, 1.0),
    "staccato": (65, 0.25),
    "accent": (95, 0.85),
    "flutter": (72, 1.0),
    "breath": (50, 0.9),
    "trill": (70, 0.5),
}

# Synthesis: PhaseModSynth or AirPipe (physical aerophone model)
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.2,
    "attack": 0.04,      # Faster attack than concert flute due to shorter air column
    "release": 0.10,
}

AIR_PIPE_DEFAULTS = {
    "pressure": 0.65,    # Higher jet pressure for narrow overblowing flue pipe
    "stopped": False,
    "length_scale": 0.5, # Piccolo tube is half the length of concert flute
}

# Production
REVERB_TAIL = 2.2        # High piercing transients bloom in acoustic hall reverb
EQ_BODY = (1200, 2.0)    # Warmth in 1-2 kHz band
EQ_PRESENCE = (3500, 3.0)# Air brilliance and articulation bite
EQ_AIR = (10000, 2.0)    # Breath/chiff airiness
PAN = 0.15               # Orchestral woodwind seating (usually sits near 1st/2nd flutes, slightly off-center)


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
