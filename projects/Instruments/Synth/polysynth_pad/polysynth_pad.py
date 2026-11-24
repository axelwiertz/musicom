# -*- coding: utf-8 -*-
"""Pad 3 (polysynth) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM90 "Pad 3 (polysynth)" is the classic ANALOG POLYSYNTH pad —
the Roland Juno-106/JX-8P, Oberheim OB-X, Sequential Prophet-5, Korg
Poly-61 family: a stack of detuned saw/triangle oscillators through a
resonant low-pass filter with a slow attack and wide ensemble chorus. The
polysynth pad sits between the KB's two existing synth pads: GM88 "Pad 1
(new age)" is bright/digital glass, GM89 "Pad 2 (warm)" is dark/round
analog; GM90 is the MIDDLE of the analog pad range — rounder and slower
than the new-age shimmer, but with MORE mid presence and a faster attack
than the warm pad (the classic "strings/pad" preset of 80s pop ballads,
synthwave chords, and Detroit techno pads).

Synthesis note: this is the ONE instrument in the KB whose GM name IS the
engine — `sound/synthesis/polysynth.py` PolyVoice (polyBLEP subtractive:
3 oscillators + multimode filter + ADSR + unison) is the exact physical
model of the analog polysynth pad. PRIMARY engine is polysynth. Additive
(detuned harmonic stack, slow swell) is the pad-family secondary;
PhaseModSynth is the FM tertiary.

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
instruments and has NO polysynth constant — use the raw GM number 90; the
registry is the full KB.
"""

MIDI_PROGRAM = 90
GM_NAME = "Pad 3 (polysynth)"
# RenderPipeline stem label: GM_PROGRAMS[90] = "Pad 3 (polysynth)" -> sanitized
# stem file trackXX_Pad_3_polysynth.wav (parens stripped, spaces -> _).
STEM_LABEL = "Pad_3_polysynth"

# MIDI ranges (sounding pitch; the GM pad patch plays the whole keyboard,
# but the idiomatic pad-writing band is C2–C7 — see empirical sweep in
# instrument.md)
RANGE_MIN = 36      # C2 — sub-pad bottom (below this it's mud, not music)
RANGE_MAX = 96      # C7 — top (above C7 the patch thins to noise shimmer)
SOLO_RANGE = (55, 84)   # G3–C6 — solo-pad focus (mid body + first air)
SWEET_SPOT = (60, 84)   # C4–C6 — chord-pad zone: fullest analog body

# Register zones
ZONES = {
    "low": (36, 55),     # C2–G3, sub/mid-bass pad — roots, drone bottom
    "mid": (56, 79),     # G3–G5, primary chord-pad body — the workhorse band
    "high": (80, 96),    # G5–C7, analog top — rounder than the new-age
                         #   shimmer (the filter rolls the saw stack off)
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
    "bloom": (66, 1.25),    # extra-long swell — the analog pad's signature
                            #   "bloom" tail (holds past the bar, feeds verb)
}

# Synthesis engine recommendation
SYNTHESIS = "polysynth"  # sound/synthesis/polysynth.py PolyVoice — the
                         #   polyBLEP subtractive architecture (3 osc +
                         #   24dB multimode filter + ADSR + unison): the
                         #   EXACT physical model of the analog polysynth
                         #   pad (Juno/OB-X/Prophet saw stack + resonant
                         #   low-pass + slow attack + ensemble chorus) —
                         #   the one KB instrument whose GM name IS the engine
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",        # the analog pad core: detuned saw stack
    "osc2_waveform": "saw",
    "osc2_detune_cents": 7.0,      # ±7 cents — the classic ensemble width
    "osc3_waveform": "triangle",   # soft round layer — the pad body (rounder
                                   #   than synth_brass_1's square sub)
    "osc3_detune_cents": -7.0,
    "osc3_level": 0.7,
    "filter_cutoff": 1800.0,       # low-pass — between warm_pad 1400 and
                                   #   synth_brass_1 2800: rounder than the
                                   #   warm pad but with more mid presence
    "filter_resonance": 0.3,       # gentle peak — body, not squelch
    "env_attack": 0.35,            # slow swell (between synth_strings_1 0.03
                                   #   and warm_pad 0.45 — pads ENTER, they
                                   #   don't stab)
    "env_decay": 0.2,
    "env_sustain": 0.85,
    "env_release": 0.6,            # slow fade — pad tails into the reverb
    "unison_voices": 4,            # 4 detuned voices = the wide chorus blur
}
SYNTHESIS_DEFAULTS = {
    "instrument": "polysynth_pad",
    **POLYSYNTH_DEFAULTS,
}

# Additive secondary — the pad-family engine (synth_pad/warm_pad precedent):
# detuned harmonic stack with slow swell, DARKER rolloff than new-age.
ADDITIVE_HARMONICS = {
    "pad_polysynth": [1.0, 0.75, 0.55, 0.38, 0.25, 0.15, 0.09],
}
ADDITIVE_DEFAULTS = {
    "attack": 0.35,
    "detune": 0.012,
    "stack": 4,
    "release": 0.6,
    "sustain_level": 0.9,
    "decay_S": 1e-4,    # pad recipe MUST hold the chord (2026-10-12 additive
                        #   quirk: apply_overtones leaves frequency at the
                        #   top partial — decay_S ~1e-4 per grid step)
}

# PhaseModSynth tertiary — the FM pad alt (gentle depth: polysynth ≠ brassy)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.8,       # between warm 1.5 and synth_brass_1 3.2 — the
                            #   analog pad fattens, never honks
    "attack": 0.4,
    "release": 0.6,
    "sustain_level": 0.85,
}

# Modal fallback — generic struck-string bank, least faithful (only for
# short plucked "blip" effects, NOT the sustained pad)
MODAL_PRESET = "string"

# Production defaults
REVERB_TAIL = 3.0       # seconds — same as warm_pad: the analog pad blooms
                        #   in a big hall but keeps body (new-age 88 needs
                        #   the full 3.2 air wash; the polysynth pad is
                        #   rounder, so 3.0 keeps it grounded)
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — the saw stack + triangle sub
                        #   piles the low-mid fast (same cut as warm_pad)
EQ_PRESENCE = (2800, 2.0)  # peaking boost Hz, dB — the mid BODY band: the
                           #   polysynth pad speaks in the 2–3 kHz presence,
                           #   brighter than warm_pad's 2400 (more saw edge)
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — GENTLE top air (the low-pass
                        #   rolls the saw stack off by design; contrast
                        #   new-age 9.5 kHz +2.0)
PAN = 0.0               # center for the composed stem; ±0.4 L/R spread on
                        #   wide stereo swells (same as the other pads)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
