# -*- coding: utf-8 -*-
"""Xylophone — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with a custom XYLOPHONE_MODES bank. The orchestral
xylophone bar is ROSEWOOD, and its classic partial structure is the arch
tuning 1 : 3 : 6 (fundamental, 12th = octave+fifth, 17th ≈ 3 octaves) — the
rosewood equivalent of the vibraphone's 1 : 4 : 10 aluminium arch. The stock
'marimba' preset (harmonic 1:2:3 stack, decay rates 8–20) is the wrong
partial structure AND the wrong decay for xylophone: the 3rd partial is a
discarded overtone in xylophone tuning, not an octave. KARPLUS_DEFAULTS
(loop_gain 0.9935) is the demoted fallback — the bar is struck, not plucked,
so a KS waveguide only approximates the bright short ring.

Identity: GM13 = orchestral xylophone (rosewood bars, resonator tubes,
hard polyball / rattan mallets) — the bright, cutting, dry ancestor of the
marimba (1 octave higher, hollow/arch partials, very short ring). NOT the
folk "xylophone" toy (glockenspiel = steel bars, GM9).
"""

MIDI_PROGRAM = 13
GM_NAME = "Xylophone"
# RenderPipeline stem label: GM_PROGRAMS[13] = "Xylophone" -> stem file
# trackXX_Xylophone.wav (matches exactly, no quirk; FluidR3 preset 13 =
# "Xylophone")
STEM_LABEL = "Xylophone"

# MIDI ranges (standard 4-octave concert xylophone, sounding pitch — bars are
# NOT transposing; written pitch = sounding pitch)
RANGE_MIN = 53      # F3 — bottom bar of a standard 4-octave xylophone
RANGE_MAX = 89      # F6 — top bar (4 octaves above the F3 floor)
SOLO_RANGE = (60, 84)   # C4–C6 — solo repertoire / concerto focus
SWEET_SPOT = (67, 86)   # G4–D6 — brightest cutting ring, where the arch
                        # partials (3x, 6x) stay inside the SF2 sampling span

# Register zones
ZONES = {
    "low": (53, 64),     # F3–E4 — bottom bars: woody knock, weakest ring
    "mid": (65, 76),     # F4–E5 — primary melodic register, balanced cut
    "high": (77, 89),    # F5–F6 — bright brittle clatter, maximal cut
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "single_stroke": (82, 0.5),   # standard polyball stroke — bright, dry
    "roll": (64, 2.0),            # measured mallet roll — sustained legato
                                  #   (the xylophone's only sustain)
    "double_stop": (74, 0.8),     # two mallets together — dry 2-note chord
    "glissando": (70, 0.25),      # thumb/wedge slide up the bars — ripple
    "wood_block": (90, 0.2),      # rim/knock stroke on the bar edge — pure
                                  #   knock, no tone (percussive accent)
}

# Synthesis engine recommendation
SYNTHESIS = "modal"   # ModalSynth impulse-excited resonator bank
XYLOPHONE_MODES = [
    # Arch-tuned rosewood bar: f0, 3rd partial (~octave + fifth), ~6x
    # (near 3 octaves, slightly compressed by the arch cut). Ratios follow
    # the classic xylophone bar tuning 1 : 3 : 6. Decay is a RATE (per the
    # ModalSynth convention — higher = faster): rosewood bars are dry and
    # brittle — a ~0.4 s ring, the SHORT end of the melodic-percussion set
    # (marimba 8–20, vibraphone 0.30–1.10, timpani 0.9–3.0).
    (440.0, 1.00, 9.0),     # fundamental — dominant (rosewood, hard mallet)
    (1320.0, 0.42, 14.0),   # 3x — arch partial (octave + fifth), cuts hard
    (2640.0, 0.20, 20.0),   # ~6x — near-3-octave partial, compressed flat
                            #   by the arch cut; brittle attack color
]
MODAL_PRESET = "marimba"  # closest stock bank (impulse-excited bars), but
                          # WRONG partial structure (harmonic) + too-slow
                          # decay — custom XYLOPHONE_MODES is the real voice

# Karplus-Strong fallback (bar is struck, not plucked — demoted)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9935,    # short bright ping — xylophone ring ~0.4 s is
                            #   the SHORTEST of the struck/plucked set
                            #   (kalimba 0.9940, banjo 0.9960, koto 0.9970)
    "width": 0.30,          # narrow stereo spread (single-row dry bars)
    "role": "lead",
}

# Phase-mod alternative patch (cheap xylophone)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 7.0,
    "mod_depth": 1.2,
    "attack": 0.001,
    "release": 0.25,
}

# Production defaults
REVERB_TAIL = 0.9       # seconds — xylophone is the DRIEST melodic
                        #   instrument in the KB; tight room only, hall mud
                        #   smears the clatter into noise
EQ_BODY = (200, -1.5)   # peaking cut Hz, dB — light clean-up only; rosewood
                        #   body is tight, little boxiness to tame
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — polyball attack + 3x
                           #   arch partial cut
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — brittle clatter air (beyond
                        #   marimba's 8.5 kHz — xylophone is higher-pitched)
PAN = 0.0               # center for solo; single-row bars pan narrow,
                        #   +0.15..0.25 spread for ensembles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
