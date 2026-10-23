# -*- coding: utf-8 -*-
"""Synth Bass 1 — musicom instrument constants.

GM38 = Synth Bass 1 (GM1 spec; Roland GS "Synth Bass 1 (analog)",
Yamaha XG "SynthBass1"). The classic monophonic analog synth bass —
VCO (saw/square) through a resonant low-pass filter with an ADSR that
re-opens the filter on each note. The foundational bass voice of
electronic/pop/disco/funk/acid production (Roland TB-303, Minimoog,
MC-202 lineage). Distinct from the plucked Electric Bass (finger)
GM33: there is no string — the tone is an oscillator + filter.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 38
GM_NAME = "Synth Bass 1"
# RenderPipeline stem label: GM_PROGRAMS[38] = "Synth Bass 1" -> sanitized
# trackXX_Synth_Bass_1.wav (FluidR3 preset 38 = "Synth Bass 1" — match)
STEM_LABEL = "Synth_Bass_1"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — sub-bass floor of the GM patch
RANGE_MAX = 84       # C5 — practical ceiling (patches play the full
                     #   keyboard; above C5 the tone thins to a squeak)
SOLO_RANGE = (31, 60)   # G1–C4 — melodic synth-bass lines, the pocket
                        #   where octave-displacement riffs speak
SWEET_SPOT = (38, 62)   # D2–D4 — the groove zone: root-fifth pocket,
                        #   disco octave lines, filter-sweep riffs

# Register zones
ZONES = {
    "sub": (24, 35),      # C1–E2 — sub-bass fundamental zone: chest thump,
                          #   felt more than heard, single notes only
    "groove": (36, 50),   # E2–D3 — primary rhythm register: root-fifth
                          #   pocket, walking synth lines, filter envelope
    "mid": (51, 62),      # D#3–D4 — octave-displacement riffs (the disco
                          #   octave trick), melodic fills, singing tone
    "high": (63, 84),     # D#4–C5 — bright lead-bass/acid squelch register,
                          #   cutting, thin; accents and solos
}

# Articulation defaults (velocity, duration_factor)
# Synth bass articulations map to playing gestures, not string techniques:
# the "note length" IS the filter-envelope gate (a synth bass note ends
# when the gate closes, not when a string decays).
ARTICULATIONS = {
    "legato": (68, 1.0),       # sustained gate — pad-like held bass notes
    "staccato": (74, 0.35),    # short gated 16ths — disco/funk lock groove
    "accent": (96, 0.6),       # hard filter-envelope accent — the downbeat
                              #   squelch that kicks the groove
    "glide": (64, 1.0),        # portamento between notes (TB-303 slide —
                              #   the "acid" glue; requires portamento on
                              #   the synth, pitch-bend in MIDI)
    "squelch": (88, 0.5),      # filter-resonance squelch — 303-style
                              #   resonance peak on the attack
    "octave_jump": (80, 0.4),  # octave-displacement riff hit — the disco
                              #   bass signature (A2-A3-A2-A3)
    "ghost": (40, 0.15),      # muted/closed-gate tick — rhythmic filler,
                              #   no real pitch
}

# Synthesis engine recommendation
SYNTHESIS = "mono_synth"  # sound/synthesis/mono_synth.py MonoSynth —
                          # subtractive monophonic VCO → 24dB ladder
                          # filter → ADSR. The EXACT architecture of the
                          # classic analog bass (MC-202/AD-202 lineage).
SYNTHESIS_DEFAULTS = {
    "waveform": "saw",           # saw VCO = the classic analog bass core
    "sub_level": 0.3,            # sub-oscillator one octave down = fatness
    "filter_cutoff": 1800.0,     # low-pass opens the saw, tames harshness
    "filter_resonance": 0.55,    # moderate peak — the squelch band
    "filter_env_amount": 0.5,    # per-note filter re-open = the pluck
    "filter_keytrack": 0.5,      # keep timbre consistent across registers
    "env_a": 0.005,              # near-instant VCA attack (the gate click)
    "env_d": 0.18,               # fast decay into the sustain body
    "env_s": 0.75,               # sustained while the gate is open
    "env_r": 0.12,               # quick release — tight, no wash
    "saturation": 0.15,          # gentle analog drive on the VCA output
    "drift_amount": 0.002,       # per-voice analog drift
}
MODAL_PRESET = "string"   # modal resonator fallback (generic plucked body)

# PhaseModSynth alternative (FM synth-bass patch — the DX7 "Solid Bass" /
# cheap analog emulation)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,   # fundamental modulation — fattens the saw
    "mod_depth": 2.5,
    "attack": 0.005,
    "release": 0.12,
}

# Karplus-Strong tertiary (plucked-waveguide "rubber band" analog emulation
# — not the physical model, but a usable string-free bass approximation)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,    # moderate damping — tight rubbery thump
    "lowpass_hz": 1500.0,   # dark: the filter IS the synth-bass voice
    "excitation": "pluck",
    "role": "bass",
}

# Production defaults
REVERB_TAIL = 1.0        # seconds, small room/plate — synth bass is
                         #   almost always dry (DI); verb is a mix choice,
                         #   never baked in; 1.0 s room for exposed lines
EQ_BODY = (250, -2.5)    # peaking cut Hz, dB — reduce low-mid mud where
                         #   the saw + sub pile up against the kick
EQ_PRESENCE = (900, 2.0) # peaking boost Hz, dB — the filter-sweep
                         #   "growl" band (finger-attack analogue)
EQ_AIR = (6000, 1.0)     # highshelf Hz, dB — gentle air; synth bass is
                         #   dark by design, no top-octave sparkle needed
PAN = 0.0                # center — bass is universally mono/centered


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
