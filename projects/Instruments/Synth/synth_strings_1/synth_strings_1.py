# -*- coding: utf-8 -*-
"""Synth Strings 1 (GM50) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM50 "Synth Strings 1" is the **divide-down string machine** — the
1972–1982 keyboard class (Eminent 310 Unique, ARP Solina String Ensemble,
ARP Omni, Roland RS-202, Korg Poly-Ensemble, Elka Rhapsody, Logan String
Melody, Crumar Performer). One divide-down oscillator bank feeds a shared
filter and a shared LFO, and a TRIPLE BBD ENSEMBLE CHORUS provides the
signature slow, wide, slightly-detuned swirl. It is paraphonic, not truly
polyphonic: all held notes share the same chorus phase. No velocity
sensitivity, no bow noise, infinite sustain while held, short capacitor
release.

Siblings (do not confuse): GM48 String Ensemble 1 and GM49 String Ensemble 2
are the sampled *acoustic* sections — realistic, rosin, bow articulation.
GM50 is the *synthetic* one: brighter, wider, obviously processed. This entry
fills the GM50/51 pair's first slot (GM51 Synth Strings 2 is the slower/airier
variant, still open).

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
programs and has NO synth-strings constant — use the raw GM number 50; the
registry is the full KB.

Synthesis note: primary is PolySynth (the subtractive divide-down + shared
filter + unison detune IS the physical model); Additive is the cheap
harmonic-stack bed; PhaseModSynth saw-carrier is the tertiary approximation.
"""

MIDI_PROGRAM = 50
GM_NAME = "Synth Strings 1"
# RenderPipeline stem label: GM_PROGRAMS[50] = "Synth Strings 1" -> sanitized
# stem file trackXX_Synth_Strings_1.wav (spaces -> _). Exact match, no quirk.
STEM_LABEL = "Synth_Strings_1"

# MIDI ranges (sounding pitch; the GM patch plays the whole keyboard, but the
# idiomatic string-machine band is C2–C7 — original machines were 4-octave,
# 49-key. Below C2 the divider tone turns to mud; above C7 it thins to fizz.)
RANGE_MIN = 36      # C2 — pad bottom (below this: mud, not music)
RANGE_MAX = 96      # C7 — top (above C7 the patch thins to band-limited fizz)
SOLO_RANGE = (52, 88)   # E3–E6 — solo string-machine band (chorus + buzz)
SWEET_SPOT = (60, 84)   # C4–C6 — chord-pad zone: fullest body + chorus swirl

# Register zones
ZONES = {
    "low": (36, 55),     # C2–G3, cello-ish body — pad roots, drone bottom
    "mid": (56, 79),     # G#3–G5, primary pad/harmony body — the workhorse
    "high": (80, 96),    # G#5–C7, violin-top sheen — thin, band-limited fizz
}

# Articulation defaults (velocity, duration_factor). NOTE: real string
# machines have NO velocity sensitivity — velocity here mainly scales loudness;
# the GM patch barely changes timbre. Write dynamics via density/register.
ARTICULATIONS = {
    "sustain": (70, 1.0),   # held pad chord — the default gesture
    "legato": (68, 1.0),    # overlapping chord change, no re-attack click
    "swell": (82, 1.0),     # slow crescendo build — the machine's "expression"
    "staccato": (66, 0.25), # short chord stab — disco/synth-pop chop
    "marcato": (86, 0.85),  # hard downbeat chord, chorus blooms after
    "drone": (58, 1.0),     # static held harmony — ambient/modal bed
    "accent": (90, 0.9),    # unison hit, then sustain
}

# Synthesis engine recommendation
SYNTHESIS = "polysynth"  # sound/synthesis/polysynth.py — divide-down saw/square
                         #   bank + shared low-pass + BBD ensemble chorus
ADDITIVE_HARMONICS = {
    # Bright buzzy string-machine stack: strong 2nd–6th partials, band-limited
    # top (BBD rolls off ~6–8 kHz). Weights RELATIVE (drawbar-style); normalize
    # to sum 1.0 before apply_overtones() (the API asserts sum == 1.0).
    "string_machine": [1.0, 0.85, 0.70, 0.55, 0.40, 0.28, 0.18, 0.10],
}
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",        # the bright divide-down core
    "osc2_waveform": "square",     # divider buzz edge (the string-machine bite)
    "osc2_detune_cents": 9.0,      # one side of the ensemble chorus
    "osc3_waveform": "saw",        # second detuned layer, opposite side
    "osc3_detune_cents": -9.0,
    "osc3_level": 0.8,             # thick: 3-voice BBD blur
    "filter_cutoff": 3000.0,       # band-limited BBD top (warm_pad 1400,
                                   #   synth_brass_1 2800 — this is brighter)
    "filter_resonance": 0.2,       # mild peak — body, not squelch
    "env_attack": 0.03,            # fast-but-soft capacitor onset (20–40 ms)
    "env_decay": 0.05,
    "env_sustain": 1.0,            # INFINITE hold while key down — no natural
                                   #   decay (the defining string-machine trait)
    "env_release": 0.25,           # short capacitor fade (100–300 ms)
    "unison_voices": 3,            # triple BBD ensemble = the swirl
}
SYNTHESIS_DEFAULTS = {
    "instrument": "synth_strings_1",
    "attack": 0.03,      # capacitor onset — NOT the bowed 0.35 s swell
    "detune": 0.010,     # ±1.0% per voice — wider than string_ensemble ±0.6%,
                         #   narrower than warm_pad ±1.5%
    "stack": 3,          # 3 detuned voices = triple BBD chorus
    "release": 0.25,     # short capacitor fade
    "sustain_level": 1.0,
    "decay_S": 1e-4,     # hold the chord (additive quirk: apply_overtones
                         #   leaves frequency at the top partial, so a
                         #   sustained pad recipe needs decay_S ~1e-4)
}
MODAL_PRESET = "string"  # generic resonator fallback (plucked-string bank);
                         #   least faithful — the buzz is in the oscillators
# PhaseModSynth tertiary — cheap string-machine approximation (gentle, not
# brassy: this is a string patch, not a horn)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.2,
    "attack": 0.03,
    "release": 0.3,
    "sustain_level": 1.0,
}

# Production defaults
REVERB_TAIL = 2.8       # seconds — between string_ensemble 2.6 and warm_pad
                        #   3.0: the chorus supplies width, the hall depth
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — chord mass piles up low-mid
EQ_PRESENCE = (3200, 2.0)  # peaking boost Hz, dB — divider-buzz articulation
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — BBD top is dull; a little air
                        #   restores it, but do NOT chase sampled sparkle
                        #   (synth_pad 9.5 kHz +2.0 is a different voice)
PAN = 0.0               # center for the composed stem; the patch is already
                        #   wide, so only ±0.2 L/R when doubling for a bigger bed


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
