# -*- coding: utf-8 -*-
"""Human Voice — musicom instrument constants.

A synthetic singing-voice virtual instrument. Unlike the GM "Choir Aahs"
(preset 52, a static pad) this is a *source-filter* model: an asymmetric
glottal-flow pulse (modified-Rosenberg / KLSYN88) drives a vocal-tract
cascade of formant resonators, with aspiration noise, a singer's formant,
and vibrato/jitter/shimmer. The engine lives in
sound/synthesis/singing_voice.py.

No GM preset reproduces this — a sound-font "voice" is a sampled choir, not
a playable model of the vocal tract. So this instrument is a SYNTHESIS
instrument: compositions route it to SingingVoice, not FluidSynth.
"""

MIDI_PROGRAM = 53             # GM "Choir Aahs" — closest sampled stand-in
                              # (used only for MIDI export; audio comes from
                              # SingingVoice, not the soundfont)
GM_NAME = "Human Voice"
# If the MIDI is ever rendered through FluidSynth, program 53 yields the
# "Choir Aahs" preset; its sanitized stem label is "Choir_Aahs".
STEM_LABEL = "Choir_Aahs"

# MIDI range (sounding): the practical sung range across voice types.
# A trained solo voice spans ~2 octaves; the engine accepts any pitch but
# this is the idiomatic register. (Below ~52 a bass, above ~84 a soprano.)
RANGE_MIN = 48      # C3 — low bass
RANGE_MAX = 84      # C6 — high soprano
SOLO_RANGE = (55, 79)   # G3-G5 — the practical "lead vocal" band
SWEET_SPOT = (60, 76)   # C4-E5 — the core pop/classical solo register

ZONES = {
    "bass":    (48, 55),   # C3-G3 — dark, chesty, power low
    "baritone": (56, 63),  # G#3-D#4 — warm, conversational
    "tenor":   (64, 71),   # E4-B4 — bright, forward, "belt" zone
    "alto":    (72, 76),   # C5-E5 — round female mid
    "soprano": (77, 84),   # F5-C6 — bright, ringing, head voice
}

# Articulations are mapped to engine parameters (not velocity/duration):
# each maps a sung gesture to (aspiration, open_quotient, vibrato depth).
ARTICULATIONS = {
    "legato":     (0.05, 0.65, 0.45),   # smooth connected — default
    "breathy":    (0.45, 0.55, 0.35),   # airy, intimate
    "pressed":    (0.02, 0.80, 0.30),   # bright, belted, tense
    "belt":       (0.08, 0.78, 0.55),   # strong, forward, loud
    "head":       (0.03, 0.60, 0.70),   # light, floaty, more vibrato
    "vibrato":    (0.04, 0.65, 0.80),   # wide operatic vibrato
}

# Synthesis engine recommendation.
SYNTHESIS = "singing_voice"   # sound/synthesis/singing_voice.py SingingVoice

# Engine defaults (feed into SingingVoice(open_quotient=..., ...)).
SYNTHESIS_DEFAULTS = {
    "voice_type": "alto",        # soprano/alto/tenor/bass/solo
    "open_quotient": 0.65,       # glottal open fraction (lower = breathier)
    "speed_quotient": 1.8,       # closure asymmetry (higher = brighter ring)
    "aspiration": 0.05,          # breath noise mix
    "vibrato_hz": 5.5,
    "vibrato_semitones": 0.45,
    "shimmer": 0.03,
}

# Production defaults.
REVERB_TAIL = 1.8       # seconds, hall — a sung lead wants space
EQ_BODY = (350, -3.0)   # cut Hz, dB — de-mud the chest register
EQ_PRESENCE = (2800, 2.5)  # boost Hz, dB — the singer's formant "ring"
EQ_AIR = (8000, 2.0)    # highshelf Hz, dB — consonant clarity / air
PAN = 0.0               # center (solo lead)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
