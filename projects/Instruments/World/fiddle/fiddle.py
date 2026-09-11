# -*- coding: utf-8 -*-
"""Fiddle — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is BowedString (friction
waveguide — sound/synthesis/bowed.py). GM110 "Fiddle" is a bowed string
instrument; the folk-fiddle timbre comes from a brighter, more aggressive
bow than concert violin: higher bow velocity, more rosin noise, and a
flatter bowing (less vibrato, more drive). The BOWED_DEFAULTS below
(bow_velocity 0.24, bow_force 1.8, noise 0.025) push the model into that
idiom. ModalSynth 'string' preset covers pizzicato/plucked passages;
PhaseModSynth saw-carrier is the cheap alt.
"""

MIDI_PROGRAM = 110
GM_NAME = "Fiddle"
# RenderPipeline stem label: GM_PROGRAMS[110] = "Fiddle" -> stem file
# trackXX_Fiddle.wav (matches exactly, no quirk; FluidR3 preset 110 =
# "Fiddle")
STEM_LABEL = "Fiddle"

# MIDI ranges (sounding pitch; concert fiddle = violin dimensions, GDAE)
RANGE_MIN = 55      # G3 — lowest open string
RANGE_MAX = 96      # C6 — practical high-positions ceiling (violin E7=103
                    #   exists but is NOT folk idiom; 96 keeps it grounded)
SOLO_RANGE = (60, 89)   # C4–A6 — solo repertoire focus (folk tunes sit
                        #   C4-E6; a few high ornaments reach A6)
SWEET_SPOT = (62, 86)   # D4–D6 — melodic core: GDAE first position + quick
                        #   shifts; brightest drive and clearest articulation

# Register zones
ZONES = {
    "low": (55, 61),     # G3–B3 — dark open-G register; drones, double
                         #   stops, low accompaniment
    "mid": (62, 77),     # D4–F5 — primary melodic register (tune zone)
    "high": (78, 96),    # F#5–C6 — bright, singing, cutting; ornaments
                         #   (grace notes, high kicks) live here
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (80, 1.0),   # long bow — steady folk line
    "drive": (84, 0.9),     # heavy bow, aggressive attack — dance tune
    "staccato": (68, 0.25), # short separated bow strokes
    "spiccato": (74, 0.125),# bouncing bow — reel/céilidh rhythmic pattern
    "tremolo": (70, 0.06),  # rapid bow changes — tension/ornament
    "pizzicato": (58, 0.2), # plucked — bluegrass/old-time style
    "accent": (92, 0.9),    # hard bow dig — downbeat punch
    "grace": (66, 0.05),    # cut/grace note — idiom ornament
}

# Synthesis engine recommendation
SYNTHESIS = "bowed"   # BowedString friction waveguide (SP-024)
BOWED_DEFAULTS = {
    "bow_velocity": 0.24,   # higher than concert violin (0.2) — folk drive
    "bow_force": 1.8,       # firm contact, aggressive attack
    "bow_position": 0.15,   # standard violin bow point
    "noise_level": 0.025,   # rosin scratch — folk fiddles are noisy
}
MODAL_PRESET = "string"  # modal resonator fallback (pizzicato/pluck)

# Phase-mod alternative patch (cheap fiddle)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.5,
    "attack": 0.02,
    "release": 0.1,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, room/plate — folk clarity; shorter than
                        #   concert violin 2.0 (dance music needs dry cut)
EQ_BODY = (400, -2.0)   # peaking cut Hz, dB — tame wooden-body boxiness
EQ_PRESENCE = (2800, 2.5)  # peaking boost Hz, dB — bow attack + rosin
EQ_AIR = (7500, 1.5)    # highshelf Hz, dB — airless, not sterile; fiddle
                        #   projects on the mid, not the 9k+ shimmer
PAN = 0.0               # center solo; +0.15..0.3 in ensemble/twin-fiddle


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)