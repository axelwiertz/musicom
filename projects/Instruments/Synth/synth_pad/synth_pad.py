# -*- coding: utf-8 -*-
"""Synth Pad (Pad 1 new age) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM88 "Pad 1 (new age)" is the classic slow-attack digital synth pad
(Roland D-50-era LA synthesis: detuned osc stack + chorus + long swell) — the
"Synth Pad" voice that orchestration.md's Pad role lists alongside "Strings
(sustained)" and "Organ". The KB previously had the acoustic/orchestral pad
voices (church organ, string ensemble) but NO synthesizer pad — meanwhile
composition jobs (Arabic 235/071, Ambient evolving v1, Experimental 044)
were already sending `MidiInstrument.SYNTH_PAD` for the Pad voice with no KB
entry behind it.

Enum note: `structures/instrument.py` `MidiInstrument.SYNTH_PAD = 88` — for
once the enum value matches the raw GM program (registry is still the full
KB for every other instrument; 88 here is genuinely "Pad 1 (new age)").

Synthesis note: primary is Additive (detuned harmonic stack with slow swell
— the same engine family as the organ/string-ensemble pads, but wider
detune for the synth chorus and a faster-than-strings attack). The
PhaseModSynth saw-stack is the classic analog-pad alternative (FM_DEFAULTS).
"""

MIDI_PROGRAM = 88
GM_NAME = "Pad 1 (new age)"
# RenderPipeline stem label: GM_PROGRAMS[88] = "Pad 1 (new age)" -> sanitized
# stem file trackXX_Pad_1_new_age.wav (parens stripped, spaces -> _).
STEM_LABEL = "Pad_1_new_age"

# MIDI ranges (sounding pitch; the GM pad patch plays the whole keyboard,
# but the idiomatic pad-writing band is C2–C7 — see empirical sweep in
# instrument.md)
RANGE_MIN = 36      # C2 — sub-pad bottom (below this it's mud, not music)
RANGE_MAX = 96      # C7 — top (above C7 the patch thins to noise shimmer)
SOLO_RANGE = (55, 84)   # G3–C6 — solo-pad focus (mid body + first shimmer)
SWEET_SPOT = (60, 84)   # C4–C6 — chord-pad zone: fullest body + air balance

# Register zones
ZONES = {
    "low": (36, 55),     # C2–G3, sub/mid-bass pad — roots, drone bottom
    "mid": (56, 79),     # G3–G5, primary chord-pad body — the workhorse band
    "high": (80, 96),    # G5–C7, shimmer top — new-age sparkle, upper octaves
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (70, 1.0),   # slow-swelling pad — the default gesture
    "legato": (68, 1.0),    # seamless voice crossfade — chord changes
    "swell": (82, 1.0),     # crescendo swell — whole-bar build (Enya trick)
    "staccato": (64, 0.25), # short pad "blip" — rhythmic filter-pulse motif
    "marcato": (85, 0.85),  # attack override — plucked/bell onset (D-50 style)
    "drone": (60, 1.0),     # static sustained harmony — ambient bed
    "accent": (88, 0.9),    # hard entrance — downbeat hit, then bloom
}

# Synthesis engine recommendation
SYNTHESIS = "additive"   # sound/synthesis/additive.py SoundWave — the pad
                         #   IS a detuned harmonic stack (organ/string-ens
                         #   engine precedent, wide chorus detune for synth)
ADDITIVE_HARMONICS = {
    # Warm stack: strong fundamental, gentle rolloff, air on top
    "pad_warm": [1.0, 0.8, 0.6, 0.45, 0.3, 0.2, 0.12],
    # New-age stack: airier, more shimmer weight up high (D-50 "glass")
    "pad_newage": [1.0, 0.65, 0.5, 0.35, 0.22, 0.15, 0.1, 0.06],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "synth_pad",
    "attack": 0.55,      # slow swell (0.4–1.0 s real synth-pad onset) — the
                         #   SLOWEST family onset: strings 0.35, this 0.55,
                         #   ambient swells up to 1.0
    "detune": 0.012,     # ±1.2% per voice — double the string section chorus
                         #   (±0.006): the synth "ensemble" width is the point
    "stack": 4,          # 4 detuned voices per note = the classic pad blur
    "release": 0.5,      # slow fade — pad tails into the reverb
    "sustain_level": 0.9,
}
# Classic analog-pad alternative (saw stack, subtle PM, slow envelope)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.0,
    "attack": 0.6,
    "release": 0.5,
    "sustain_level": 0.85,
}

# Production defaults
REVERB_TAIL = 3.2       # seconds — LONGEST in the KB (string ens 2.6, harp
                        #   2.2): the synth pad is the quintessential
                        #   "bloom in a big hall/ambient space" voice
EQ_BODY = (300, -3.0)   # peaking cut Hz, dB — clear low-mid pile-up
                        #   (synth chords stack 250–400 Hz fast)
EQ_PRESENCE = (3800, 2.5)  # peaking boost Hz, dB — shimmer/presence
EQ_AIR = (9500, 2.0)    # highshelf Hz, dB — the new-age AIR is the identity
                        #   (contrast: string ensemble cuts 8.5k — the pad
                        #   WANTS sparkle)
PAN = 0.0               # center for the composed stem; ±0.4 L/R spread on
                        #   wide stereo swells (double the strings ±0.3)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)