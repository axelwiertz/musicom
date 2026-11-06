# -*- coding: utf-8 -*-
"""Warm Pad (Pad 2 warm) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM89 "Pad 2 (warm)" is the classic WARM ANALOG synth pad — a
detuned oscillator stack (triangle/saw) through a low-pass filter with a
slow attack and wide chorus: the 80s ballad / synthwave / ambient bed
(Roland Juno-60 "D50" warm programs, Oberheim OB-X pads, Vangelis
"Charlots of Fire" beds, M83 / Tame Impala warmth). The DARK sibling of
synth_pad GM88 "Pad 1 (new age)": where new-age is bright/digital glass
(air + shimmer), warm is rounder and darker — a stronger fundamental,
weaker high partials, wider chorus, gentler top. FluidR3 preset 89 =
"Warm Pad" (the synth_pad entry's "darker sibling" — this entry).

Synthesis note: primary is Additive (detuned harmonic stack with slow
swell — the pad-family engine, synth_pad/string_ensemble/organ
precedent) with a DARKER stack than pad_newage (faster rolloff, weaker
high partials). Secondary is Polysynth (the polyBLEP subtractive
architecture IS the analog warm-pad model: triangle/saw stack through a
LOW cutoff ~1400 Hz). PhaseModSynth is the tertiary FM-pad alt (gentle
depth 1.5 — warm pads are NOT brassy).

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
instruments and has NO warm-pad constant — use the raw GM number 89; the
registry is the full KB.
"""

MIDI_PROGRAM = 89
GM_NAME = "Pad 2 (warm)"
# RenderPipeline stem label: GM_PROGRAMS[89] = "Pad 2 (warm)" -> sanitized
# stem file trackXX_Pad_2_warm.wav (parens stripped, spaces -> _).
STEM_LABEL = "Pad_2_warm"

# MIDI ranges (sounding pitch; the GM pad patch plays the whole keyboard,
# but the idiomatic pad-writing band is C2–C7 — see empirical sweep in
# instrument.md)
RANGE_MIN = 36      # C2 — sub-pad bottom (below this it's mud, not music)
RANGE_MAX = 96      # C7 — top (above C7 the patch thins to noise shimmer)
SOLO_RANGE = (55, 84)   # G3–C6 — solo-pad focus (mid body + first air)
SWEET_SPOT = (60, 84)   # C4–C6 — chord-pad zone: fullest warm body

# Register zones
ZONES = {
    "low": (36, 55),     # C2–G3, sub/mid-bass pad — roots, drone bottom
    "mid": (56, 79),     # G3–G5, primary chord-pad body — the workhorse band
    "high": (80, 96),    # G5–C7, warm top — rounded, NOT the new-age
                         #   shimmer (rolls off vs pad_1's sparkle)
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (70, 1.0),   # slow-swelling pad — the default gesture
    "legato": (68, 1.0),    # seamless voice crossfade — chord changes
    "swell": (82, 1.0),     # crescendo swell — whole-bar build (ballad trick)
    "staccato": (64, 0.25), # short pad "blip" — rhythmic filter-pulse motif
    "marcato": (85, 0.85),  # attack override — plucked/bell onset
    "drone": (60, 1.0),     # static sustained harmony — ambient bed
    "accent": (88, 0.9),    # hard entrance — downbeat hit, then bloom
    "bloom": (66, 1.25),    # extra-long swell — the warm pad's signature
                            #   "bloom" tail (holds past the bar, feeds verb)
}

# Synthesis engine recommendation
SYNTHESIS = "additive"   # sound/synthesis/additive.py SoundWave — the pad
                         #   IS a detuned harmonic stack (synth_pad /
                         #   string_ensemble / organ engine precedent),
                         #   with a DARKER stack than the new-age pad
ADDITIVE_HARMONICS = {
    # Warm stack: strong fundamental, FASTER rolloff than pad_newage —
    #   the warmth is the low-mid body, the top is rounded not sparkling.
    #   Weights are RELATIVE (drawbar-style); normalize to sum 1.0 before
    #   apply_overtones() (the API asserts the factors sum to 1.0).
    "pad_warm": [1.0, 0.78, 0.58, 0.40, 0.26, 0.15, 0.08],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "warm_pad",
    "attack": 0.45,      # between string ensemble 0.35 and synth_pad 0.55 —
                         #   warm swells a touch faster than new-age glass
    "detune": 0.015,     # ±1.5% per voice — WIDER than synth_pad ±0.012:
                         #   the analog chorus IS the warm identity
    "stack": 3,          # 3 detuned voices (synth_pad uses 4 — fewer voices
                         #   = less top brightness, rounder body)
    "release": 0.6,      # slow fade — pad tails into the reverb
    "sustain_level": 0.9,
    "decay_S": 1e-4,     # per-grid-step decay (the 2026-10-12 additive
                         #   quirk: apply_overtones leaves frequency at the
                         #   top partial, so a pad recipe MUST use decay_S
                         #   ~1e-4 to hold a long chord)
}
# Analog-pad alternative: the polyBLEP subtractive architecture IS the
# physical model (Juno/OB-X warm pad: triangle/saw stack + LOW cutoff)
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "triangle",   # the warm core — triangle is rounder
                                   #   than saw (the warm-pad fundamental)
    "osc2_waveform": "saw",        # chorus edge
    "osc2_detune_cents": 7.0,
    "osc3_waveform": "saw",        # second detuned layer, opposite side
    "osc3_detune_cents": -7.0,
    "osc3_level": 0.7,
    "filter_cutoff": 1400.0,       # LOW cutoff — the darkness IS the point
                                   #   (synth_brass_1 uses 2800; warm pad
                                   #   sits at half that)
    "filter_resonance": 0.35,      # gentle peak — body, not squelch
    "env_attack": 0.45,            # slow swell (analog pad onset)
    "env_decay": 0.3,
    "env_sustain": 0.8,
    "env_release": 0.6,
    "unison_voices": 3,            # 3 detuned voices = the chorus blur
}
# PhaseModSynth tertiary — the FM pad alt (gentle depth: warm ≠ brassy)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.5,
    "attack": 0.5,
    "release": 0.6,
    "sustain_level": 0.85,
}

# Production defaults
REVERB_TAIL = 3.0       # seconds — between string_ensemble 2.6 and
                        #   synth_pad 3.2: the warm pad blooms in a big
                        #   hall but keeps more body than the new-age
                        #   shimmer (which needs the full 3.2 air wash)
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — the strong fundamental
                        #   piles the low-mid FAST (cut a touch LOWER than
                        #   synth_pad's 300: warmth = more fundamental mass)
EQ_PRESENCE = (2400, 2.0)  # peaking boost Hz, dB — the warm BODY band
                           #   (contrast new-age 3.8 kHz: warm pads speak
                           #   in the low-mid presence, not the shimmer)
EQ_AIR = (7500, 1.5)    # highshelf Hz, dB — GENTLE top air (contrast
                        #   new-age 9.5 kHz +2.0: warmth rolls the top off
                        #   by design)
PAN = 0.0               # center for the composed stem; ±0.4 L/R spread on
                        #   wide stereo swells (same as synth_pad)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
