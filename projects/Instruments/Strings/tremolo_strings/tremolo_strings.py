# -*- coding: utf-8 -*-
"""Tremolo Strings — musicom instrument constants.

GM44 = Tremolo Strings (GM1 spec program 45 "Tremolo Strings"; Roland GS
"Tremolo Strings", Yamaha XG "TremoloStrings"). The bowed STRING SECTION
playing rapid repeated bow strokes — the film-score tension texture (the
famous "bathroom mirror" cue, every thriller underscore). Distinct from
String Ensemble 1 (GM48, sustained section bows) and Pizzicato Strings
(GM45, plucked section): the section is bowed and the bow NEVER stops —
the note is a continuous chattering tremolo.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the section-chorus timbre is an additive detuned harmonic
stack (the String Ensemble 1 precedent); the tremolo itself is NOT a
synthesis-engine parameter in musicom — BowedString/Additive have no
internal tremolo. Write tremolo at the note layer (fast repeated strokes
or a long note + 7 Hz AM at the production layer); the FluidR3 patch
already carries deep built-in amplitude modulation (measured ripple ~1.0).
"""

MIDI_PROGRAM = 44
GM_NAME = "Tremolo Strings"
# RenderPipeline stem label: GM_PROGRAMS[44] = "Tremolo Strings" -> stem
# file trackXX_Tremolo_Strings.wav (matches exactly, no quirk; FluidR3
# preset 44 = "Tremolo" — one-word SF2 spelling, cosmetic only)
STEM_LABEL = "Tremolo_Strings"

# MIDI ranges (sounding pitch; full string-section span, empirical FluidR3
# sweep: preset 44 audible 24–96 (C1–C7, every note rms 0.030–0.045),
# SILENT at 108+ — never write above C7=96)
RANGE_MIN = 24      # C1 — contrabass bottom (audible in the GM patch)
RANGE_MAX = 96      # C7 — violin-top ceiling (patch is silent above)
SOLO_RANGE = (53, 89)   # F3–A6 — solo-section focus (cello-to-violin lead)
SWEET_SPOT = (60, 84)   # C4–C6 — violin/viola lead zone, the tremolo
                        #   chatters cleanest (low registers blur into rumble)

# Register zones
ZONES = {
    "low": (24, 47),     # C1–B2, contrabass/cello register — rumbling
                        #   tension bottom; use sparingly, blurs fast
    "mid": (48, 71),     # C3–B4, viola/cello middle — harmonic body,
                        #   the underscore workhorse
    "high": (72, 96),    # C5–C7, violin top — cutting, glassy, chattering
                        #   accent tension (sul ponticello zone)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "tremolo": (72, 1.0),   # the patch default: sustained rapid bow strokes,
                           #   steady chattering intensity
    "sustain": (74, 1.0),  # regular bowed section notes (the GM patch
                           #   tremolos regardless of articulation — the
                           #   sample itself is amplitude-modulated)
    "sul_ponticello": (80, 0.9),  # bow near the bridge — glassy, brighter,
                           #   cutting tension accent
    "staccato": (66, 0.25), # short separated bow bursts — rhythmic tension
    "accent": (92, 0.9),    # hard sforzando dig — the downbeat stab
    "crescendo": (78, 1.4), # roll/swell into a peak — the surge-and-release
                           #   underscore staple (longer duration)
}

# Synthesis engine recommendation
SYNTHESIS = "additive"   # sound/synthesis/additive.py SoundWave — section
                         #   chorus = detuned harmonic stack (String
                         #   Ensemble 1 precedent)
ADDITIVE_HARMONICS = {
    # Dense partial stacks (many detuned strings per section voice)
    "section_full": [1.0, 0.9, 0.7, 0.5, 0.35, 0.25, 0.18],
    "section_sul": [1.0, 0.6, 0.4, 0.25, 0.15, 0.1, 0.05],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "tremolo_strings",
    "attack": 0.02,      # tremolo bow is ALREADY moving — near-instant
                         #   re-articulation, no slow bow onset
    "detune": 0.006,     # ±0.6% per voice — section chorus, not one string
    "stack": 3,          # 3 detuned voices per note = section spread
    "release": 0.20,     # bows cut together on release, quick stop
    "tremolo_hz": 7.0,   # production-layer AM rate: the tremolo itself
                         #   (write repeated 16ths/32nds at the note layer,
                         #   or AM a long note at 7 Hz — the patch already
                         #   carries deep built-in AM, ripple ~1.0)
}
MODAL_PRESET = "string"  # modal resonator fallback (section pizzicato)

# Single-string alternative (BowedString models ONE string, not a section)
BOWED_DEFAULTS = {
    "bow_velocity": 0.26,   # tremolo bowing is FASTER and more driven than
                            #   concert sustain (fiddle 0.24, section 0.2)
    "bow_force": 1.6,       # firm contact — the chattering grip
    "bow_position": 0.12,   # slightly toward the bridge for edge
    "noise_level": 0.015,   # low-mid rosin — section blend stays smooth
}
# Cheap "string machine" alt (classic 70s ensemble synth + AM tremolo)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.8,
    "attack": 0.02,
    "release": 0.2,
}

# Production defaults
REVERB_TAIL = 2.4       # seconds, hall — tension texture needs space to
                        #   bloom (between string_ensemble 2.6 and violin
                        #   2.0); 2.4 s keeps the chattering attack defined
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — clear low-mid mud (section
                        #   mass piles up 200–400 Hz, tremolo doubles it)
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — bow-stroke articulation
                        #   bite (the chattering attack band)
EQ_AIR = (8500, 1.5)    # highshelf Hz, dB — subtle air; section is warm,
                        #   a wall of 9k+ shimmer is a production artifact
PAN = 0.0               # center; ±0.3 L/R for wide section spread


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
