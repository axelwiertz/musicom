# -*- coding: utf-8 -*-
"""Synth Voice — musicom instrument constants.

GM54 = "Synth Voice" (GM1 spec; Roland GS "Synth Voice", Yamaha XG
"SynthVoice"). The classic ANALOG/DIGITAL synthesizer "choir": a detuned
saw/square oscillator stack shaped by a vowel (formant) filter, with a slow
breathy attack and a delayed LFO vibrato — the "aaah" voice of 70s/80s
synth music (Roland VP-330 choir preset, Yamaha CS-80 "voice", Korg M1 voice
programs; Vangelis Blade Runner, Jean-Michel Jarre Oxygene, Tangerine Dream,
synthwave leads). It is a SYNTH voice, not a sampled choir — the tone is
oscillators + formant filter, no real singers (contrast GM52 Choir Aahs, the
sampled chorus).

Distinct from the Vocal family (human_voice / choir — sampled/formant-synth
SINGERS): GM54 is a synthesizer lead/pad that *reads as* a voice. Family
Synth, alongside synth_pad (GM88) and synth_brass_1 (GM62).

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 54
GM_NAME = "Synth Voice"
# RenderPipeline stem label: GM_PROGRAMS[54] = "Synth Voice" -> sanitized
# trackXX_Synth_Voice.wav (FluidR3 preset 54 = "Synth Voice" — exact match)
STEM_LABEL = "Synth_Voice"

# MIDI ranges (sounding pitch; the GM synth-voice patch plays the full
# keyboard — empirical FluidR3 sweep 24–108 all audible, no gaps — the band
# below is the idiomatic WRITING register: C2–C7)
RANGE_MIN = 36       # C2 — sub bottom (below C2 the oscillator stack is mud)
RANGE_MAX = 96       # C7 — top (above C7 the formants smear to noise shimmer)
SOLO_RANGE = (60, 84)   # C4–C6 — solo voice-lead zone: the "singing" band
SWEET_SPOT = (55, 79)   # G3–G5 — vocal-register heart: melody + pad chords

# Register zones
ZONES = {
    "low": (36, 55),      # C2–G3 — dark pad bottom: chord roots, drone beds
    "mid": (56, 71),      # G3–C5 — workhorse band: melody, chord body
    "high": (72, 84),     # C5–C6 — voice-lead top: the Blade Runner register
    "top_extension": (85, 96),  # C6–C7 — thin shimmer, riser sparkle
}

# Articulation defaults (velocity, duration_factor)
# Synth-voice articulations map to singing gestures: the held "ah" is the
# signature; the slow attack IS the articulation (contrast the sampled choir,
# which attacks with breath, and a stab patch, which punches).
ARTICULATIONS = {
    "ah": (72, 1.0),        # sustained open-vowel lead — THE default gesture
    "legato": (70, 1.0),    # seamless voice crossfade — phrase joins
    "swell": (60, 1.15),    # crescendo on a held note — filter opens (Jarre
                            #   Oxygene move: the voice blooms in)
    "marcato": (85, 0.85),  # hard onset — accented entrance, word-like attack
    "staccato": (74, 0.30), # short gated blips — rhythmic voice stabs
    "vibrato": (76, 1.0),   # lead with LFO vibrato (delayed ~1.5 s; MIDI CC1/
                            #   aftertouch — SF2 presets often have built-in)
    "accent": (88, 0.9),    # downbeat hit, then bloom — the "ah!" entrance
    "decay_fade": (58, 1.0),# phrase-end taper — the voice recedes into reverb
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"  # sound/synthesis/phase_mod.py PhaseModSynth — a
                         #   formant-ish FM voice: saw carrier, sine modulator
                         #   at the fundamental (ratio 1.0) creates the
                         #   "vocal" sideband stack; slow attack = the breath
FM_DEFAULTS = {
    "carrier_shape": "saw",    # the oscillator-choir core (CS-80/VP-330 voice)
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,     # fundamental modulation — fattens the saw into
                               #   a vowel-like stack (brass uses 1.0 too but
                               #   deeper; the voice keeps it mild)
    "mod_depth": 2.6,          # between synth_pad 2.0 and synth_brass_1 3.2 —
                               #   a voice is softer than a horn, edgier than
                               #   a pad (the "presence" of the vowel)
    "attack": 0.25,            # slow breathy onset (50–300 ms real voice leads)
    "release": 0.35,           # medium tail — the voice recedes, not cuts
    "sustain_level": 0.85,     # held while the gate is open
}
SYNTHESIS_DEFAULTS = {
    "instrument": "synth_voice",
    **FM_DEFAULTS,
}

# Additive alternative — formant-weighted harmonic stacks (choir.py precedent:
# partials near the vowel formants are boosted; here the same recipe but with
# the synth "saw-singer" brightness on top)
ADDITIVE_DEFAULTS = {
    "harmonic_count": 8,
    # "ah" vowel (F1 730 / F2 1090 / F3 2440 Hz): formant bump on partials 2–4,
    # more top weight than the real choir (the SYNTH voice is brighter)
    "harmonic_weights": [1.0, 0.78, 0.62, 0.55, 0.40, 0.28, 0.18, 0.10],
    "attack": 0.25,
    "release": 0.35,
}

# Polysynth fallback — the subtractive oscillator-choir: saw + square stack
# through a low-pass with a slow gate (the "analog voice pad" architecture)
POLYSYNTH_DEFAULTS = {
    "osc1_waveform": "saw",
    "osc2_waveform": "saw",
    "osc2_detune_cents": 6.0,    # slight detune = the choral "section" width
    "osc3_waveform": "square",
    "osc3_level": 0.2,
    "filter_cutoff": 3200.0,     # formant-ish band: let the vowel through
    "filter_resonance": 0.6,     # vowel peak — the "ah" honk band
    "filter_env_amount": 0.4,    # per-note filter open = the swell gesture
    "env_attack": 0.25,          # slow breathy onset
    "env_decay": 0.3,
    "env_sustain": 0.85,
    "env_release": 0.35,
    "unison_voices": 3,          # 3 detuned voices = the synth "choir" width
}

# Production defaults
REVERB_TAIL = 2.8        # seconds — hall/plate: the voice blooms in a space;
                         #   same as choir 2.8 (a voice is ALWAYS in a room),
                         #   shorter than synth_pad 3.2 (leads keep presence)
EQ_BODY = (350, -2.5)    # peaking cut Hz, dB — oscillator stack + vowel
                         #   formants pile up in the low-mid (mud) fast
EQ_PRESENCE = (2400, 2.0)  # peaking boost Hz, dB — the vowel "presence" band
                           #   (F3 2440 Hz region — intelligibility of the "ah")
EQ_AIR = (8500, 1.5)     # highshelf Hz, dB — gentle top air; the synth voice
                         #   is bright but not sibilant (cut 8k = hiss)
PAN = 0.0                # center for the composed stem; ±0.3 L/R spread on
                         #   wide doubled-lead swells


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
