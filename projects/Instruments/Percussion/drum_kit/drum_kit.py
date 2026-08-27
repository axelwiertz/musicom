# -*- coding: utf-8 -*-
"""Drum Kit — musicom instrument constants (GM channel 9 percussion)."""

MIDI_PROGRAM = 0
CHANNEL = 9          # 0-indexed GM percussion channel
GM_NAME = "Channel 10 (percussion)"
# RenderPipeline stem label quirk: channel 9 with program 0 → labeled
# "Acoustic_Grand_Piano" (program-0 fallback). The stem IS drums.
STEM_LABEL = "Acoustic_Grand_Piano"

# Standard kit mapping (MIDI note → role)
KIT = {
    "kick": 36,      # BASS_DRUM
    "snare": 38,     # ACOUSTIC_SNARE
    "clap": 39,      # HAND_CLAP
    "hat_closed": 42,
    "tom_low": 45,
    "tom_mid": 47,
    "crash": 49,
    "tom_high": 50,
    "ride": 51,
    "cowbell": 56,
    "maracas": 70,
    "claves": 75,
    "woodblock": 76,
}

# Typical velocity per part
VELOCITIES = {
    "kick": 100,
    "snare": 90,
    "clap": 90,
    "hat_closed": 65,
    "tom_low": 80,
    "tom_mid": 80,
    "crash": 95,
    "tom_high": 80,
    "ride": 70,
    "cowbell": 85,
    "maracas": 60,
    "claves": 85,
    "woodblock": 80,
}

# Synthesis recommendation
SYNTHESIS = "drum_machine"   # DrumMachine in sound/effects/tape_delay.py
MODAL_PRESET = "drum"

# Grid alignment (16th note)
STEP16_TICKS = 120   # at 480 TPB, 4/4


def beat_pattern(beats_per_bar: int = 4, beat_indices=(0, 4, 8, 12)) -> list:
    """16-step beat pattern: 1 at given 16th indices (0,4,8,12 = beats)."""
    return [1 if i in beat_indices else 0 for i in range(16)]
