# -*- coding: utf-8 -*-
"""Synth Strings 2 (GM51) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM51 "Synth Strings 2" is the SAME 1972–1982 divide-down string
machine family as GM50 (Eminent 310, ARP Solina, Roland RS-202, Korg
Poly-Ensemble, Elka Rhapsody) but the *slow-swell / airy* variant: softer
onset, fuller low-mid body, and a rolled-off top instead of GM50's bright
divider fizz. Measured on FluidR3_GM (identical Cmaj7 chord, solo):

  preset 50: centroid 1738 Hz (mid) / 717 Hz (low) / 2727 Hz (high)
  preset 51: centroid 1853 Hz (mid) / 1487 Hz (low) / 2361 Hz (high)

i.e. GM51 keeps ~2x the upper-partial energy in the BASS register (1487 vs
717 Hz centroid) and loses top-octave fizz (2361 vs 2727 Hz) — the "keeps
definition down low, never gets shrill up top" pad. Onset is softer (env at
20 ms = 0.12 of peak vs 0.16) and the patch is ~0.8 dB louder.

Siblings (do not confuse): GM48/49 are sampled *acoustic* sections, GM50 is
the bright string machine, GM51 is this slower/airier variant, GM88/89/90
are the New-Age/Warm/Polysynth pads (no divide-down chorus character).

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
programs and has NO synth-strings constant — use the raw GM number 51; the
registry is the full KB.

Synthesis note: primary is PolySynth (divide-down bank + shared filter +
BBD ensemble chorus IS the physical model); Additive is the cheap
harmonic-stack bed; PhaseModSynth saw-carrier is the tertiary approximation.
"""

MIDI_PROGRAM = 51
GM_NAME = "Synth Strings 2"
# RenderPipeline stem label: GM_PROGRAMS[51] = "Synth Strings 2" -> sanitized
# stem file trackXX_Synth_Strings_2.wav (spaces -> _). Exact match, no quirk.
STEM_LABEL = "Synth_Strings_2"

# MIDI ranges (sounding pitch). Original machines were 4-octave/49-key; the
# GM patch plays the whole keyboard, but below C2 the divider turns to mud and
# above C7 the band-limited top thins to fizz. GM51 tolerates the LOW register
# better than GM50 (measured 1487 Hz vs 717 Hz centroid at C2–E3).
RANGE_MIN = 36      # C2 — pad bottom
RANGE_MAX = 96      # C7 — top
SOLO_RANGE = (48, 86)   # C3–D6 — solo band: chorus swirls, body stays clear
SWEET_SPOT = (55, 84)   # G3–C6 — chord-pad zone: fullest body, no fizz

# Register zones
ZONES = {
    "low": (36, 55),     # C2–G3, cello-ish body — pad roots, drone bottom
                         #   (GM51's clear low-mid is its main edge over GM50)
    "mid": (56, 79),     # G#3–G5, primary pad/harmony body — the workhorse
    "high": (80, 96),    # G#5–C7, soft sheen — rolled off, never shrill
}

# Articulation defaults (velocity, duration_factor). Real string machines
# have NO velocity sensitivity; velocity here mainly scales loudness. GM51's
# slower onset means swells read better than stabs — write dynamics as
# arrangement (density/register), not as hard/soft playing.
ARTICULATIONS = {
    "sustain": (70, 1.0),   # held pad chord — the default gesture
    "legato": (68, 1.0),    # overlapping chord change, no re-attack click
    "swell": (84, 1.0),     # slow crescendo build — GM51's signature gesture
    "bloom": (76, 0.9),     # soft entry that opens over ~0.4 s
    "staccato": (62, 0.25), # short chop — weaker on GM51 (soft onset)
    "marcato": (82, 0.85),  # downbeat chord, chorus blooms after
    "drone": (56, 1.0),     # static held harmony — ambient/cinematic bed
    "accent": (88, 0.9),    # unison hit, then sustain
}

# Synthesis engine recommendation
SYNTHESIS = "polysynth"  # sound/synthesis/polysynth.py — divide-down bank +
                         #   shared low-pass + BBD ensemble chorus
ADDITIVE_HARMONICS = {
    # Softer, rounder stack than GM50's "string_machine": weaker 6th–8th
    # partials (the measured top-octave roll-off). Weights RELATIVE
    # (drawbar-style); normalize to sum 1.0 before apply_overtones()
    # (the API asserts sum == 1.0).
    "string_machine_airy": [1.0, 0.82, 0.64, 0.48, 0.34, 0.22, 0.12, 0.06],
}
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",        # divide-down core (softer than GM50's set)
    "osc2_waveform": "saw",        # second detuned layer — no square edge:
    "osc2_detune_cents": 11.0,     #   GM51 is the rounder sibling
    "osc3_waveform": "triangle",   # body filler, opposite chorus side
    "osc3_detune_cents": -11.0,
    "osc3_level": 0.75,
    "filter_cutoff": 2700.0,       # between warm_pad 1400 and GM50's 3000:
                                   #   dark top, but not dull
    "filter_resonance": 0.25,      # a touch more peak than GM50 (0.2) for
                                   #   the low-mid body that defines GM51
    "env_attack": 0.09,            # slower swell than GM50 0.03 —
                                   #   measured softer initial transient
    "env_decay": 0.08,
    "env_sustain": 1.0,            # infinite hold while key down
    "env_release": 0.45,           # airier capacitor fade than GM50 0.25
    "unison_voices": 3,            # triple BBD ensemble = the swirl
}
SYNTHESIS_DEFAULTS = {
    "instrument": "synth_strings_2",
    "attack": 0.09,      # slow-swell onset — the defining GM51 trait
    "detune": 0.012,     # ±1.2% per voice — wider than GM50 ±1.0%,
                         #   narrower than warm_pad ±1.5%
    "stack": 3,          # 3 detuned voices = triple BBD chorus
    "release": 0.45,     # airier tail than GM50 (0.25)
    "sustain_level": 1.0,
    "decay_S": 1e-4,     # hold the chord (additive quirk: apply_overtones
                         #   leaves frequency at the top partial, so a
                         #   sustained pad recipe needs decay_S ~1e-4)
}
MODAL_PRESET = "string"  # generic resonator fallback (plucked-string bank);
                         #   least faithful — the buzz is in the oscillators
# PhaseModSynth tertiary — cheap approximation; gentler than GM50's 1.2 depth
# (GM51 is the darker sibling, do not add brightness here)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 0.9,
    "attack": 0.09,
    "release": 0.5,
    "sustain_level": 1.0,
}

# Production defaults
REVERB_TAIL = 3.4       # seconds — longer than GM50's 2.8: slower onset +
                        #   darker top = cinematic/ambient bed, needs the hall
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — trim chord mass, less than GM50
                        #   (-2.5) because GM51 already keeps its low-mid body
EQ_PRESENCE = (2600, 1.5)  # peaking boost Hz, dB — articulation lift under
                           #   the darker filter (GM50 lifts 3.2 kHz +2.0)
EQ_AIR = (9000, 1.0)    # highshelf Hz, dB — GM51 rolls off up top by design;
                        #   add a little air, do not chase GM50's fizz
PAN = 0.0               # center for the composed stem; the BBD chorus is
                        #   already wide, so only ±0.2 L/R when doubling


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
