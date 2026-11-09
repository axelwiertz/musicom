# -*- coding: utf-8 -*-
"""Orchestra Hit — musicom instrument constants.

GM55 = "Orchestra Hit" (GM2 spec; Roland GS "Orchestra Hit", Yamaha XG
"Orchestra Hit"; also known as "Orchestral Hit"). The iconic ONE-SHOT
ensemble stab: a dense layered stack of brass + strings + choir samples
(or synthesized equivalent) fired with a razor-sharp attack and a fast
exponential decay — the "stab" that punctuates 80s pop, hip-hop, film
trailers and game scores (Yes "Owner of a Lonely Heart", the MTV/network
ident stabs, countless beat drops). There is NO sustain: the sample
fires once per note-on and decays; a long MIDI note just holds the
decayed tail.

Distinct from the sustained Synth family (synth_pad GM88, warm_pad GM89,
synth_brass_1 GM62, synth_voice GM54): GM55 is a PERCUSSIVE one-shot —
the attack transient IS the instrument. Family Synth, role accent/stab.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 55
GM_NAME = "Orchestra Hit"
# RenderPipeline stem label: GM_PROGRAMS[55] = "Orchestra Hit" -> sanitized
# trackXX_Orchestra_Hit.wav (FluidR3 preset 55 = "Orchestra Hit" — match)
STEM_LABEL = "Orchestra_Hit"

# MIDI ranges (sounding pitch; GM one-shot patch plays the whole keyboard —
# empirical FluidR3 sweep 36–96 all audible, smooth rolloff 1345→374 RMS,
# no gaps, no ceiling — the band below is the idiomatic WRITING register)
RANGE_MIN = 36       # C2 — sub-hit floor (below C2 the stack is mud-thump)
RANGE_MAX = 96       # C7 — top (above C7 the hit thins to a tick)
SOLO_RANGE = (48, 84)   # C3–C6 — the hit zone: downbeat stabs, drops,
                        #   punctuation hits
SWEET_SPOT = (55, 79)   # G3–G5 — the classic "orchestra hit" register:
                        #   fullest stack, cleanest transient

# Register zones
ZONES = {
    "low": (36, 47),      # C2–B2 — sub-hit thump: riser bottoms, drop
                         #   punctuation (mud below C2)
    "mid": (48, 71),      # C3–B4 — the workhorse stab band: downbeat hits,
                         #   syncopated punctuation, beat-drop stabs
    "high": (72, 84),     # C5–C6 — bright top hits: cinematic stabs,
                         #   octave-doubled punctuation
    "top_extension": (85, 96),  # C6–C7 — thin sparkle hits, riser ticks
}

# Articulation defaults (velocity, duration_factor)
# Orchestra-hit articulations map to STRIKE gestures: the "hit" IS the
# signature (one-shot — the sample fires once per note-on and decays; the
# MIDI note length only delays the next strike, it does not sustain).
ARTICULATIONS = {
    "hit": (96, 0.20),      # THE signature: one-shot ensemble stab —
                            #   the 80s/hip-hop/trailer punctuation
    "accent": (104, 0.10),  # hard downbeat smash — the "1" of the drop
    "stab": (90, 0.15),     # syncopated rhythmic stab — off-beat punches
    "sfz": (100, 0.12),     # sforzando hit — maximum attack, then cut
    "repeat": (85, 0.25),   # rapid retriggers — 8th/16th hit patterns
                            #   (each note-on re-fires the sample)
    "swell": (78, 0.5),     # held hit — the decaying tail rings into verb
    "light": (70, 0.20),    # soft tap — ghost punctuation, riser accents
    "tick": (60, 0.10),     # dry tick — sparse top-register punctuation
}

# Synthesis engine recommendation
SYNTHESIS = "additive"  # sound/synthesis/additive.py SoundWave — the
                        #   classic recipe IS a dense harmonic stack with
                        #   a razor attack + fast exponential decay (the
                        #   layered brass+strings+choir sample stack,
                        #   synthesized), plus a noise transient for the
                        #   "hit" edge. Fast decay = one-shot behaviour.
ADDITIVE_HARMONICS = {
    # Dense bright ensemble stack: strong fundamental, slow rolloff — the
    # layered brass+strings+choir wall. Weights are RELATIVE; normalize to
    # sum 1.0 before apply_overtones() (the API asserts sum == 1.0).
    "orchestra_hit": [1.0, 0.88, 0.75, 0.60, 0.45, 0.32, 0.20, 0.12],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "orchestra_hit",
    "attack": 0.005,      # razor attack — the sample-snappy transient IS
                         #   the instrument (5 ms, fastest in the Synth set)
    "release": 0.35,      # medium tail — the decaying stack rings briefly
    "sustain_level": 0.35,  # one-shot: the stack decays, it does not hold
    "decay_S": 0.002,     # FAST per-grid-step decay — the hit collapses
                         #   (contrast the pads' 1e-4 hold recipe)
    "detune": 0.008,      # slight detune = the ensemble "section" width
    "stack": 3,           # 3 detuned voices = the layered-sample wall
}

# PhaseModSynth secondary — the FM ensemble stab (bright brass-ish edge,
# fast gate). A NON-integer mod ratio folds partials into the dense
# inharmonic "orchestra" splash.
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,   # fundamental modulation — fattens the saw
    "mod_depth": 3.5,        # between synth_brass_1 3.2 and overdriven
                             #   4.0 — the bright ensemble edge
    "attack": 0.005,         # razor gate (one-shot behaviour)
    "release": 0.40,
    "sustain_level": 0.30,   # decays fast — no sustain body
}

# Polysynth tertiary — the subtractive ensemble stab: saw stack through a
# high low-pass, fast gate, quick decay (the "synth orchestra" recipe)
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",
    "osc2_waveform": "saw",
    "osc2_detune_cents": 6.0,
    "osc3_waveform": "square",
    "osc3_level": 0.25,
    "filter_cutoff": 3500.0,    # high cutoff — keep the bright stack
    "filter_resonance": 0.3,
    "filter_env_amount": 0.3,
    "env_attack": 0.005,        # razor gate
    "env_decay": 0.4,           # fast collapse
    "env_sustain": 0.3,
    "env_release": 0.3,
    "unison_voices": 3,
}

# Production defaults
REVERB_TAIL = 1.8        # seconds — hall/plate: hits want PUNCH, not wash;
                         #   shorter than synth_brass_1 2.2 (a one-shot in a
                         #   3 s verb is a smear). The decayed tail rings
                         #   into the room, then stops.
EQ_BODY = (300, -2.5)    # peaking cut Hz, dB — the dense stack piles the
                         #   low-mid fast (the layered samples crowd 250–400)
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — the "stab" bite band
                           #   (the transient edge that cuts a mix)
EQ_AIR = (9000, 1.0)     # highshelf Hz, dB — gentle top air; the hit is
                         #   bright by design but the transient is a click,
                         #   not a cymbal
PAN = 0.0                # center for the composed stem; ±0.3 L/R spread on
                         #   wide doubled hits (the "big screen" width)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
