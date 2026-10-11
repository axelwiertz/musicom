# -*- coding: utf-8 -*-
"""String Ensemble 1 — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM48 "String Ensemble 1" is the sustained bowed STRING SECTION
(full complement: violins + violas + cellos (+ pizzicato-style attack
layer in the SF2 patch). This is the "Strings (sustained)" voice that
orchestration.md's Pad role references — the KB previously had solo bowed
voices (violin/viola/cello/bass/fiddle) and the plucked section
(pizzicato_strings) but NO sustained-section pad.

Synthesis note: the primary recommendation is Additive (detuned harmonic
stack = the classic section-chorus timbre — the same engine the organ KB
entry uses). A section is many slightly-detuned bowed strings; the
BowedString engine models ONE string, so it is the single-string/solo
alternative, not the section default. PhaseModSynth saw-carrier is the
cheap "string machine" alt.
"""

MIDI_PROGRAM = 48
GM_NAME = "String Ensemble 1"
# RenderPipeline stem label: GM_PROGRAMS[48] = "String Ensemble 1" -> stem
# file trackXX_String_Ensemble_1.wav (matches exactly, no quirk; FluidR3
# preset 48 = "Strings" — one-word SF2 spelling, cosmetic only)
STEM_LABEL = "String_Ensemble_1"

# MIDI ranges (sounding pitch; full string-section span)
RANGE_MIN = 28      # E1 — contrabass bottom, section bass register
RANGE_MAX = 96      # C7 — violin-top ceiling (empirical FluidR3 sweep:
                    #   preset 48 audible 24–96, SILENT at 102+, no gaps)
SOLO_RANGE = (53, 89)   # F3–A6 — solo-section focus (cello-to-violin lead)
SWEET_SPOT = (60, 84)   # C4–C6 — violin/viola lead zone, fullest section glow

# Register zones
ZONES = {
    "low": (28, 47),     # E1–B2, contrabass/cello register — pad bottom, weight
    "mid": (48, 71),     # C3–B4, viola/cello middle — primary harmonic pad body
    "high": (72, 96),    # C5–C7, violin top — cutting melody, filigree, accents
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (78, 1.0),   # long section bow — the pad default
    "legato": (74, 1.0),    # portato overlap — seamless melodic line
    "marcato": (88, 0.8),   # heavy accented bow — downbeat emphasis
    "staccato": (66, 0.25), # short separated bows — rhythmic section
    "spiccato": (72, 0.125),# bouncing bow — light rhythmic texture
    "tremolo": (70, 0.06),  # rapid bow changes — tension/underscore staple
    "sforzando": (95, 0.9), # fp accent — dramatic hit then settle
    "accent": (92, 0.9),    # hard bow dig — punch
}

# Synthesis engine recommendation
SYNTHESIS = "additive"   # sound/synthesis/additive.py SoundWave — section
                         #   chorus = detuned harmonic stack (organ precedent)
ADDITIVE_HARMONICS = {
    # Dense partial stacks (many detuned strings per section voice)
    "section_full": [1.0, 0.9, 0.7, 0.5, 0.35, 0.25, 0.18],
    "section_sul": [1.0, 0.6, 0.4, 0.25, 0.15, 0.1, 0.05],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "string_ensemble",
    "attack": 0.35,      # slow section bow onset (0.3–0.6 s real)
    "detune": 0.006,     # ±0.6% per voice — section chorus, not one string
    "stack": 3,          # 3 detuned voices per note = section spread
    "release": 0.40,     # bows lift together, gentle decay
}
MODAL_PRESET = "string"  # modal resonator fallback (section pizzicato)

# Single-string alternative (BowedString models ONE string, not a section)
BOWED_DEFAULTS = {
    "bow_velocity": 0.2,   # concert string section bow
    "bow_force": 1.5,      # standard firm contact
    "bow_position": 0.15,  # standard bow point
    "noise_level": 0.01,   # low rosin — section blend is smooth
}
# Cheap "string machine" alt (classic 70s ensemble synth)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.8,
    "attack": 0.05,
    "release": 0.3,
}

# Production defaults
REVERB_TAIL = 2.6       # seconds, hall — section pad loves space (longest
                        #   in the Strings family: violin 2.0, harp 2.2)
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — clear low-mid mud (section
                        #   mass piles up 200–400 Hz)
EQ_PRESENCE = (3200, 2.0)  # peaking boost Hz, dB — bow articulation
EQ_AIR = (8500, 1.5)    # highshelf Hz, dB — subtle air; section is warm,
                        #   a wall of 9k+ shimmer is a production artifact
PAN = 0.0               # center; ±0.3 L/R for wide section spread


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)