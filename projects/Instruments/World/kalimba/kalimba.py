# -*- coding: utf-8 -*-
"""Kalimba — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — SP-011, sound/synthesis/karplus_strong.py). A kalimba tine is a
struck metal bar — the Karplus loop models the pluck transient + decaying
partials well; loop_gain sits BELOW the sitar/koto values (0.9975/0.9970)
because metal tines ring shorter than sympathetic-string instruments, but
above the dull 0.990 floor so the ring is audible. The ModalSynth 'bell'
preset (inharmonic metal modes) is the fallback; the FM patch below is the
cheap alternative.
"""

MIDI_PROGRAM = 108
GM_NAME = "Kalimba"
# RenderPipeline stem label: GM_PROGRAMS[108] = "Kalimba" -> stem file
# trackXX_Kalimba.wav (matches exactly, no quirk; FluidR3 preset 108 = "Kalimba")
STEM_LABEL = "Kalimba"

# MIDI ranges (sounding pitch; 17-note C4-E6 core, extended/treble edges)
RANGE_MIN = 48      # C3 — extended 21-note kalimba bottom (Hugh Tracey 17-note starts C4=60)
RANGE_MAX = 96      # C7 — treble kalimba top (17-note tops at E6=76)
SOLO_RANGE = (60, 84)   # C4–C6 — solo repertoire focus (17-note core + treble reach)
SWEET_SPOT = (62, 81)   # D4–A6 — fullest tine ring + resonator warmth

# Register zones
ZONES = {
    "low": (48, 59),     # C3–B3, extended bass tines — dark, long wooden-box ring
    "mid": (60, 76),     # C4–E6, the classic 17-note body — primary melodic register
    "high": (77, 96),    # F6–C7, treble tines — bright, thin, plinky, fast decay
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (76, 1.0),     # standard thumb stroke — full tine ring + box resonance
    "roll": (66, 0.07),     # rapid alternating-thumb tremolo — sustained illusion
    "double": (72, 0.3),    # double/triple pluck — rhythmic figure, mbira style
    "damped": (48, 0.12),   # thumb rests on tine — choked, dry, percussive
    "accent": (94, 0.9),    # hard nail strike — bright attack emphasis
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # Karplus-Strong plucked waveguide (SP-011)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9940,    # moderate damping -> metal tine ring (below sitar/koto)
    "width": 0.40,          # narrow stereo spread — intimate solo voice
    "role": "lead",
}
MODAL_PRESET = "bell"  # modal resonator fallback (inharmonic metal-bar modes)

# Phase-mod alternative patch (cheap kalimba)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.7,  # inharmonic-ish ratio — metal bar partials
    "mod_depth": 2.5,
    "attack": 0.002,
    "release": 0.5,
}

# Production defaults
REVERB_TAIL = 1.8       # seconds, room/hall — wooden-box resonance, keep tine attack
EQ_BODY = (450, -2.0)   # peaking cut Hz, dB — tame boxy resonator body
EQ_PRESENCE = (3500, 2.5)  # peaking boost Hz, dB — tine sparkle + nail click
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — subtle air; high tines already bright
PAN = 0.0               # center for solo; +0.15..0.3 spread for ostinato layers


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
