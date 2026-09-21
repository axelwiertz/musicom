# -*- coding: utf-8 -*-
"""Celesta — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM 8 = Celesta (keyboard metallophone with felt hammers striking
suspended steel plates over wooden resonating boxes, patented by Auguste Mustel
in 1886; immortalized by Tchaikovsky in 'Dance of the Sugar Plum Fairy').

Sounding range: 5 octaves (modern standard orchestral models: C3 to C8, MIDI 48–108;
historic 4-octave models: C4 to C8, MIDI 60–108). In orchestral scores, the celesta
is written one octave lower (transposing octave keyboard, sounded 8va alta). In musicom
standard MIDI convention, sounding pitch is used directly (RANGE_MIN=48, RANGE_MAX=108),
while GM SoundFonts like FluidR3 respond down to MIDI 48 with smooth response.

Synthesis note:
The primary recommendation is ModalSynth (sound/synthesis/modal.py) with custom
CELESTA_MODES or stock preset='bell'. The steel plate struck by felt hammers produces
a warm fundamental coupled to wooden resonator resonance and soft inharmonic metal
overtones (decaying slower than a xylophone but warmer and less piercing than an
orchestral glockenspiel).
Karplus-Strong (loop_gain 0.9970) or PhaseModSynth (mod_ratio 2.76, mod_depth 1.1)
serve as secondary fallbacks.
"""

MIDI_PROGRAM = 8
GM_NAME = "Celesta"
# RenderPipeline stem label: GM_PROGRAMS[8] = "Celesta" -> stem file
# trackXX_Celesta.wav (matches exactly, no quirk; FluidR3 preset 8 = "Celesta", phdr-verified)
STEM_LABEL = "Celesta"

# MIDI ranges (sounding pitch; 5-octave orchestral celesta: C3–C8)
RANGE_MIN = 48       # C3 (sounding) — lowest note of modern 5-octave concert celesta
RANGE_MAX = 108      # C8 (sounding) — highest note of 5-octave concert celesta
SOLO_RANGE = (60, 96)   # C4–C7 — standard melodic / arabesque / arpeggio register
SWEET_SPOT = (72, 96)   # C5–C7 — purest celestial sparkle, bell-like timbre over wooden boxes

# Register zones (sounding pitches)
ZONES = {
    "low": (48, 59),     # C3–B3 — dark, bell-like, soft struck-steel hum
    "mid_low": (60, 71), # C4–B4 — mellow, round, warm celestial chime
    "mid_high": (72, 83),# C5–B5 — singing crystalline sweetness (Sugar Plum Fairy zone)
    "high": (84, 95),    # C6–B6 — sparkling, brilliant, ethereal chime
    "altissimo": (96, 108), # C7–C8 — delicate silver droplet pinpricks
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "normale": (78, 1.0),      # standard felt hammer strike with natural resonance decay
    "staccatissimo": (75, 0.3),# short detached touch, sparkling pointillistic drop
    "legato": (70, 1.1),       # sustained arpeggio flow, damper pedal engaged
    "accent": (95, 0.9),       # brilliant bell-like sforzato highlight
    "pianissimo": (52, 1.0),   # whisper-quiet delicate chime, mysterious atmosphere
    "arpeggio": (72, 0.85),    # rolled celestial chord / arabesque sweep
}

# Synthesis engine recommendation
SYNTHESIS = "modal"   # ModalSynth impulse-excited resonator bank
MODAL_PRESET = "bell" # Built-in stock preset in sound/synthesis/modal.py

# Custom modal modes for felt-struck steel bar over wooden resonator box (A4 reference 440 Hz)
# Ratios: 1.0 (fundamental + resonator coupling), 2.76 (transverse mode),
# 5.40 (secondary plate mode), 8.90 (high attack shimmer).
# Decay rates are moderate (3.2 to 8.5) — warmer and softer than glockenspiel (2.5–9.0).
CELESTA_MODES = [
    (440.0, 1.00, 3.2),    # f0 fundamental + wooden resonator tone, long warm ring
    (1214.4, 0.40, 4.8),   # ~2.76x — mellow steel plate inharmonic mode
    (2376.0, 0.18, 6.5),   # ~5.40x — soft metallic overtone
    (3916.0, 0.08, 8.5),   # ~8.90x — delicate felt hammer transient ping
]

# Karplus-Strong fallback
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,    # warm metallic bar decay (~1.2-2.0s)
    "width": 0.40,          # moderate stereo spread for keyboard metallophone
    "role": "lead",
}

# Phase-mod alternative patch (soft celestial bell / FM chime)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 2.76,  # inharmonic steel plate ratio
    "mod_depth": 1.1,        # gentle modulation depth (felt hammer, not metal beater)
    "attack": 0.003,         # fast felt strike onset
    "release": 1.2,          # natural plate ring
}

# Production defaults
REVERB_TAIL = 2.4         # seconds — celesta thrives in lush concert hall reverberation
EQ_BODY = (500, 1.5)      # gentle boost at 500 Hz for wooden resonator warmth
EQ_PRESENCE = (4000, 1.8) # crystalline clarity on felt hammer attack
EQ_AIR = (11000, 2.2)     # airy celestial high shimmer
PAN = 0.25                # placed to the orchestral left-center or right-rear near percussion


def midi_to_freq(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
