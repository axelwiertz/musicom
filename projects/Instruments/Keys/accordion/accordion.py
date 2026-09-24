# -*- coding: utf-8 -*-
"""Accordion — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is PhaseModSynth (free-reed
aerophone — sound/synthesis/phase_mod.py). A saw carrier with moderate
modulation reproduces the reed's buzzy richness. The accordion's
signature multi-rank chorus (musette tuning) is best simulated by
layering 2-3 PhaseModSynth voices at ±2-5 cents offset.

Identity: GM21 = piano accordion (right-hand piano keyboard + left-hand
Stradella bass/chord system). A fully polyphonic instrument — melody,
harmony, and bass all at once. NOT a monophonic lead voice.
"""

MIDI_PROGRAM = 21
GM_NAME = "Accordion"
# RenderPipeline stem label: GM_PROGRAMS[21] = "Accordion" -> stem file
# trackXX_Accordion.wav (matches exactly, no quirk; FluidR3 preset 21 =
# "Accordian" — archaic SF2 spelling, cosmetic only, no routing impact)
STEM_LABEL = "Accordion"

# MIDI ranges (full-size piano accordion, 41 keys + 120 basses)
RANGE_MIN = 36      # C2 — lowest 8' bass reed on Stradella system
RANGE_MAX = 96      # C7 — extended treble keyboard top
SOLO_RANGE = (53, 89)   # F3-F6 — full right-hand keyboard (standard 41-key)
SWEET_SPOT = (60, 84)   # C4-C6 — primary melodic register, richest reed tone

# Register zones
ZONES = {
    "bass": (36, 52),      # C2-E3 — left-hand Stradella bass row (single notes)
    "low_treble": (53, 59),  # F3-B3 — bottom of right-hand keyboard, dark/mellow
    "mid_treble": (60, 76),  # C4-E5 — primary melodic register, richest tone
    "high_treble": (77, 89), # F5-F6 — bright, cutting (piccolo/violin register)
    "extended": (90, 96),    # G6-C7 — extended top keys, thin/piercing
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (74, 1.0),    # steady bellows, held note — default
    "staccato": (78, 0.2),   # short bellows pulse, crisp release
    "bellows_shake": (82, 0.5),  # rapid bellows vibrato — amplitude tremolo
    "marcato": (86, 0.9),    # hard bellows accent, strong attack
    "legato": (65, 1.0),     # smooth connected notes, minimal bellows change
    "sforzando": (92, 0.8),  # sudden forceful bellows push
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",     # free reed = symmetric oscillator: even+odd
                                #   harmonics (like oboe/sax family)
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 3.2,           # moderate — accordion reed buzz between oboe
                                #   (2.5) and bagpipe (4.5); the multi-rank
                                #   chorus adds thickness, not extreme buzz
    "attack": 0.015,            # very fast — reed speaks instantly on airflow
    "release": 0.05,            # near-instant — reed stops on bellows reversal
}
MODAL_PRESET = "string"  # modal fallback: sustained harmonic stack, clean

# Production defaults
REVERB_TAIL = 1.4       # seconds, room — accordion is dry/close; keep reed
                        #   detail clear, avoid washout
EQ_BODY = (300, -2.5)   # peaking cut Hz, dB — tame bellows body boxiness
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — reed clarity + cut
EQ_AIR = (8000, 1.0)    # highshelf Hz, dB — subtle key-click sparkle
PAN = 0.0               # center for solo; ±0.15-0.25 spread for stereo
                        #   left-hand (bass) vs right-hand (treble)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
