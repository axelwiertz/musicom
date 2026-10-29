# -*- coding: utf-8 -*-
"""Synth Brass 1 — musicom instrument constants.

GM62 = "Synth Brass 1" (GM1 spec; Roland GS "Synth Brass 1", Yamaha XG
"SynthBrass1"). The classic analog synth brass: a stack of slightly-detuned
sawtooth oscillators through a resonant low-pass filter with a fast attack
and a punchy ADSR — the "brassy stab" voice of funk/disco/synth-pop/film
(Prophet-5 / OB-Xa brass patches, Earth Wind & Fire horn-stab emulation,
Gary Numan / Depeche Mode brass swells). Polyphonic: stabs, sustained
brass-pad chords and unison leads all idiomatic.

Distinct from the acoustic Brass family (trumpet/trombone/french_horn/
tuba/brass_section — all PhaseModSynth saw carriers): GM62 is a SYNTH brass
— the tone is an oscillator + filter, no physical instrument, and the
preferred engine is the polyBLEP subtractive polysynth (saw stack + 24dB
filter + ADSR), the exact analog-brass architecture.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 62
GM_NAME = "Synth Brass 1"
# RenderPipeline stem label: GM_PROGRAMS[62] = "Synth Brass 1" -> sanitized
# trackXX_Synth_Brass_1.wav (FluidR3 preset 62 = "Synth Brass 1" — match)
STEM_LABEL = "Synth_Brass_1"

# MIDI ranges (sounding pitch, non-transposing; GM synth patch plays the
# full keyboard — empirical FluidR3 sweep 24–108 all audible, 15/15 notes,
# no gaps — the band below is the idiomatic WRITING register)
RANGE_MIN = 36       # C2 — sub-brass floor (below C2 the saw stack is mud)
RANGE_MAX = 96       # C7 — top (above C7 the patch thins to a squeak)
SOLO_RANGE = (48, 84)   # C3–C6 — solo/lead brass zone: the stab heart
SWEET_SPOT = (55, 79)   # G3–G5 — punch zone: funk stabs, unison leads,
                        #   brass-pad chord body

# Register zones
ZONES = {
    "low": (36, 55),      # C2–G3 — brass-pad root zone: sustained chord
                         #   bottoms, drone stabs (mud below C2)
    "mid": (56, 71),      # B3–C5 — the workhorse band: stab chords,
                         #   horn-call figures, ensemble punches
    "high": (72, 84),     # C5–C6 — lead/unison brass: piercing synth top
                         #   line, octave-doubled stabs
    "top_extension": (85, 96),  # C6–C7 — thin sparkle stabs, risers
}

# Articulation defaults (velocity, duration_factor)
# Synth brass articulations map to playing gestures: the "stab" IS the
# signature (fast attack + short gate = the funk/disco horn punch), the
# sustained swell is the pad face of the patch.
ARTICULATIONS = {
    "stab": (96, 0.30),      # the signature: fast attack, short gate —
                            #   the funk/disco horn punch (EW&F, Shining Star)
    "sustain": (78, 1.0),   # brass-pad swell — held chord, filter opens
    "swell": (72, 1.15),    # crescendo swell — whole-bar build (Gary Numan)
    "legato": (74, 1.0),    # seamless lead crossfade — unison synth brass
    "marcato": (88, 0.70),  # accented entrance — downbeat punch
    "staccato": (70, 0.25), # short gated 8ths — rhythmic comp stabs
    "sfz": (100, 0.35),     # sforzando hit — hard accent, then cut
    "rip": (92, 0.20),      # rising gliss stab — film brass rip (requires
                            #   pitch-bend in MIDI; a fast chromatic run is
                            #   the SF2-compatible approximation)
}

# Synthesis engine recommendation
SYNTHESIS = "polysynth"  # sound/synthesis/polysynth.py PolyVoice — the
                         #   polyBLEP subtractive architecture (3 osc +
                         #   24dB multimode filter + ADSR): the EXACT model
                         #   of the classic analog brass (saw stack +
                         #   resonant low-pass + punchy ADSR), and
                         #   POLYPHONIC so stabs/chords work
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",       # the brass core: saw stack
    "osc2_waveform": "saw",
    "osc2_detune_cents": 7.0,     # slight detune = the analog "section"
    "osc3_waveform": "square",    # thin sub layer for body
    "osc3_level": 0.25,
    "filter_cutoff": 2800.0,      # low-pass tames the saw, keeps the edge
    "filter_resonance": 0.45,     # moderate peak — the brassy "honk" band
    "filter_env_amount": 0.35,    # per-note filter re-open = the punch
    "env_attack": 0.015,          # fast analog gate (1–20 ms brass attack)
    "env_decay": 0.18,            # quick settle into the sustain body
    "env_sustain": 0.75,          # held while the gate is open
    "env_release": 0.25,          # medium release — stabs tail cleanly
    "unison_voices": 2,           # 2 detuned voices per note = analog width
}
SYNTHESIS_DEFAULTS = {
    "instrument": "synth_brass_1",
    **POLYSYNTH_DEFAULTS,
}

# PhaseModSynth alternative — the FM brass of the acoustic Brass family
# (brass_section precedent), brighter edge for the synth character
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,   # fundamental modulation — fattens the saw
    "mod_depth": 3.2,        # between brass_section 2.8 and overdriven 4.0
                             #   — the synth brass is EDGIER than acoustic
    "attack": 0.02,          # fast analog gate
    "release": 0.25,
    "sustain_level": 0.75,
}

# Additive fallback (harmonic stack with brass-like rolloff)
ADDITIVE_DEFAULTS = {
    "harmonic_count": 8,
    "harmonic_weights": [1.0, 0.9, 0.7, 0.5, 0.35, 0.2, 0.12, 0.08],
    "attack": 0.02,
    "release": 0.25,
}

# Production defaults
REVERB_TAIL = 2.2        # seconds — hall/plate: stabs bloom, pad swells
                         #   breathe; shorter than brass_section 2.5 (synth
                         #   stabs want a drier punch than a real brass tutti)
EQ_BODY = (300, -2.5)    # peaking cut Hz, dB — clear low-mid pile-up
                         #   (the saw stack + square sub crowd 250–400 Hz)
EQ_PRESENCE = (2800, 2.5)  # peaking boost Hz, dB — the brassy bite band
                           #   (filter-resonance analogue)
EQ_AIR = (8000, 1.0)     # highshelf Hz, dB — gentle top air; synth brass
                         #   is bright by design but not a cymbal
PAN = 0.0                # center for the composed stem; ±0.3 L/R spread
                         #   on wide unison-stab doubles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
