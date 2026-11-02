# -*- coding: utf-8 -*-
"""Synth Bass 2 — musicom instrument constants.

GM39 = Synth Bass 2 (GM1 spec; Roland GS "Synth Bass 2 (acid)", Yamaha XG
"SynthBass2"). The RESONANT analog synth bass — the TB-303 acid voice: a
pulse oscillator through a self-oscillating 24dB/oct low-pass filter whose
envelope re-opens per note, plus the accent (velocity-triggered filter-env
re-trigger) and slide (portamento) gestures that define the acid idiom
(Phuture "Acid Tracks", DJ Pierre, Armando, 1981-87 Chicago). Distinct from
Synth Bass 1 (GM38, the Minimoog-ish analog bass): SB2 is the squelch —
HIGHER filter resonance, BRIGHTER filter envelope, more aggressive accent.
The foundational bass voice of acid house / techno / electro / synthwave.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 39
GM_NAME = "Synth Bass 2"
# RenderPipeline stem label: GM_PROGRAMS[39] = "Synth Bass 2" -> sanitized
# trackXX_Synth_Bass_2.wav (FluidR3 preset 39 = "Synth Bass 2" — match)
STEM_LABEL = "Synth_Bass_2"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 21       # A0 — GM patch floor (empirical FluidR3 sweep: A0
                     #   audible, 0.2533 RMS — the sub band is LOUD)
RANGE_MAX = 96       # C7 — practical ceiling: the patch plays the full
                     #   keyboard to C7 (empirical sweep: 21–96 audible,
                     #   C8 silent); above ~C5 the tone thins to a squeak
SOLO_RANGE = (48, 72)   # C3–C5 — acid-lead band: squelchy solo lines and
                        #   octave-displacement riffs that cut through
SWEET_SPOT = (36, 55)   # C2–G3 — the groove zone: acid 16th-note
                        #   sequences, root-fifth pocket, filter-sweep riffs

# Register zones
ZONES = {
    "sub": (21, 35),      # A0–E2 — sub-bass fundamental zone: chest thump,
                          #   felt more than heard, single notes only
    "groove": (36, 50),   # C2–D3 — PRIMARY register: acid 16th-note
                          #   sequences, root-fifth pocket, the squelch band
    "mid": (51, 62),      # D#3–D4 — octave-displacement riffs, melodic
                          #   fills, bright singing tone
    "high": (63, 96),     # D#4–C7 — acid-lead/solo register: cutting
                          #   resonance, thin; accents and solos only
}

# Articulation defaults (velocity, duration_factor)
# Synth bass articulations map to the TB-303 gesture vocabulary, not string
# techniques: the accent and slide ARE the acid identity (the 303's two
# extra buttons beside the note keys).
ARTICULATIONS = {
    "accent": (98, 0.60),     # velocity accent — filter-env re-trigger,
                              #   the squelch burst on the offbeat (THE acid
                              #   gesture: Phuture 16ths live on this)
    "slide": (66, 1.0),       # portamento glide into the next note — the
                              #   303 slide (tied note + slide button)
    "squelch": (90, 0.50),    # high-resonance attack — the filter peak
                              #   "wow" as the env opens
    "staccato": (76, 0.30),   # tight gated 16ths — the acid sequence
                              #   default (gate closes, note ends)
    "legato": (68, 1.0),      # sustained gate — pad-like held bass notes
    "octave_jump": (82, 0.40),# octave-displacement riff hit — house/electro
                              #   bass signature (A2-A3-A2-A3)
    "ghost": (40, 0.15),      # muted/closed-gate tick — rhythmic filler,
                              #   no real pitch
}

# Synthesis engine recommendation
SYNTHESIS = "mono_synth"  # sound/synthesis/mono_synth.py MonoSynth —
                          # subtractive VCO → 24dB ladder filter → ADSR.
                          # The EXACT architecture of the acid bass
                          # (TB-303: pulse osc + resonant 4-pole LPF).
SYNTHESIS_DEFAULTS = {
    "waveform": "pulse",      # the 303's oscillator is a pulse wave (the
                              #   saw-derived square); pulse + resonance =
                              #   the acid core
    "pulse_width": 0.5,       # ~50% duty — the classic 303 setting
    "sub_level": 0.25,        # sub one octave down = low-end weight
    "filter_cutoff": 2400.0,  # brighter than synth_bass_1 1800: the acid
                              #   voice is the RESONANT one — it lives
                              #   higher so the sweep is audible
    "filter_resonance": 0.85, # HIGH — the squelch band; near
                              #   self-oscillation (303 resonance 0–10,
                              #   players run it hot)
    "filter_env_amount": 0.8, # per-note filter re-open = the accent/wow;
                              #   bigger than SB1's 0.5 (the acid signature)
    "filter_keytrack": 0.4,   # keep timbre consistent across registers
    "env_a": 0.004,           # near-instant VCA attack (the gate click)
    "env_d": 0.22,            # fast decay into the sustain body
    "env_s": 0.70,            # sustained while the gate is open
    "env_r": 0.10,            # quick release — tight, no wash
    "saturation": 0.18,       # gentle analog drive on the VCA output
    "drift_amount": 0.002,    # per-voice analog drift
}
MODAL_PRESET = "string"   # modal resonator fallback (generic plucked body)

# PhaseModSynth alternative (FM acid — the DX-style "rubber 303" patch)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,   # fundamental modulation — fattens the pulse
    "mod_depth": 2.8,        # edgier than synth_bass_1 2.5 — the squelch
    "attack": 0.004,
    "release": 0.10,
}

# Karplus-Strong tertiary (plucked-waveguide "rubber band" acid emulation —
# not the physical model, but a usable string-free bass approximation)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9955,    # snappier than synth_bass_1 0.9960 — acid is
                            #   punchier/tighter (short rubbery thump)
    "lowpass_hz": 1800.0,   # the filter IS the synth-bass voice
    "excitation": "pluck",
    "role": "bass",
}

# Production defaults
REVERB_TAIL = 0.9        # seconds, small room/plate — acid bass is the
                         #   driest bass in the library: the 303 is a
                         #   direct-inject voice and the resonance IS the
                         #   effect; verb smears 16th-note sequences
EQ_BODY = (220, -3.0)    # peaking cut Hz, dB — reduce low-mid mud where
                         #   pulse + sub + resonance pile up against the
                         #   kick (bigger cut than SB1 — the resonance
                         #   pushes more energy into this band)
EQ_PRESENCE = (1100, 2.5) # peaking boost Hz, dB — the squelch band: the
                          #   filter peak when the env opens (~1 kHz on a
                          #   hot 303) — the acid "growl"
EQ_AIR = (6500, 1.5)     # highshelf Hz, dB — gentle air; the 303 has a
                         #   natural top roll-off, keep it musical
PAN = 0.0                # center — bass is universally mono/centered


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
