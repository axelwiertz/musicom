# -*- coding: utf-8 -*-
"""Guitar Harmonics — musicom instrument constants.

GM 31 = Electric Guitar (harmonics). The guitar's *chiming* voice: the string
is not plucked into full vibration but touched at a node (12th / 7th / 5th
fret) so only one upper partial survives, or a fretted note is excited by a
pick harmonic (artificial / pinch harmonic). The result is a near-pure,
bell-like tone that floats an octave or more above the written pitch and
rings far longer than a normally plucked note.

This is the ice-intro / ambient layer of rock and metal, the shimmer in
impressionist and film scoring, and the "harp" color of the guitar family —
the only KB guitar voice whose fundamental is NOT the string fundamental.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

TRANSPOSITION QUIRK (measured 2026-11-13): FluidR3_GM.sf2 preset 31 is
sampled one octave above the written note — writing MIDI 60 (C4) sounds
C5 (523 Hz), verified against preset 25 and preset 105 which both sound
at written pitch. `TRANSPOSE_SEMITONES = 12` documents this: write an
octave BELOW the pitch you want to hear, exactly like a natural harmonic
at the 12th fret sounds an octave above the stopped string.
"""

MIDI_PROGRAM = 31
GM_NAME = "Guitar Harmonics"
# RenderPipeline stem label: GM_PROGRAMS[31] = "Guitar harmonics" ->
#   stem file trackXX_Guitar_harmonics.wav (pipeline uses the GM2 spec
#   spelling with a lowercase "h"; FluidR3 preset 31 = "Guitar Harmonics" —
#   cosmetic capitalisation only, no routing impact). STEM_LABEL matches the
#   pipeline's real label so stem-file lookups work.
STEM_LABEL = "Guitar_harmonics"

# SoundFont patch sounds this many semitones above the written note.
TRANSPOSE_SEMITONES = 12

# MIDI ranges — WRITTEN pitch (what you put in the MIDI file). Sounding pitch
# is written + 12 (the SF2 patch transposes; see TRANSPOSE_SEMITONES).
RANGE_MIN = 40      # written E2  -> sounds E3  (52)
RANGE_MAX = 84      # written C6  -> sounds C7  (96); patch is SILENT >= 86
SOLO_RANGE = (48, 76)   # written C3–E5 -> sounds C4–E6, the real harmonic
                        #   span of a 22-fret guitar
SWEET_SPOT = (52, 72)   # written E3–C5 -> sounds E4–C6, fullest chime: the
                        #   7th/5th-fret harmonics on the middle strings

# Register zones (written pitch; add 12 for sounding pitch)
ZONES = {
    "low": (40, 47),     # E2–B2 -> E3–B3 — 12th-fret harmonics on the wound
                         #   bass strings: fullest, woodiest chime, long ring
    "mid": (48, 64),     # C3–E4 -> C4–E5 — THE harmonic zone: 7th/5th/4th
                         #   fret nodes on A/D/G strings, primary melody
    "high": (65, 84),    # F4–C6 -> F5–C7 — artificial/pinch harmonics and
                         #   high node positions: glassy, thin, very long ring
}

# Articulation defaults (velocity, duration_factor)
# Durations are long on purpose: a node-touched string loses almost no energy
# to the other partials, so harmonics ring far longer than open-string notes.
ARTICULATIONS = {
    "harmonic_12": (84, 1.6),      # 12th-fret node — octave harmonic, the
                                   #   default natural harmonic, fullest tone
    "harmonic_7": (82, 1.4),       # 7th-fret node — octave+fifth harmonic
                                   #   (patch adds its own octave on top)
    "harmonic_5": (78, 1.4),       # 5th-fret node — double-octave harmonic,
                                   #   thinner and brighter than the 12th
    "artificial": (80, 1.0),       # fretted note + pick harmonic 12 frets up
                                   #   (any pitch reachable, melody-capable)
    "pinch_squeal": (92, 0.6),     # high-gain pinch harmonic — short screaming
                                   #   chime, the rock/metal accent
    "harp_harmonic": (70, 2.0),    # cascading harmonic arpeggio/glissando —
                                   #   the "harp" texture of the guitar
    "chime_double_stop": (74, 1.2), # two harmonics together (3rd/4th/6th
                                   #   intervals stay clean, no beating)
    "tap_harmonic": (60, 0.4),     # tapped harmonic, short and bell-like
    "let_ring": (68, 2.5),         # struck then left — full symmetric ring
    "muted": (40, 0.2),            # palm-damped harmonic ghost note
}

# Synthesis engine recommendation
SYNTHESIS = "modal"   # ModalSynth (sound/synthesis/modal.py): a node-touched
                      # string is a bank of very few, very slowly damped
                      # partials — exactly what a resonator bank models.
                      # Even partials are GONE (the node kills them), so the
                      # spectrum is the ODD series of the sounding pitch:
                      # 1f, 3f, 5f, 7f. Measured on the FluidR3 solo render:
                      # peaks at 2x/6x/10x/14x of the written note = 1x/3x/5x/7x
                      # of the sounding (octave-up) pitch.
GUITAR_HARMONICS_MODES = [
    # (freq at A4 reference, amplitude, decay RATE — higher = faster)
    (440.0, 1.00, 0.35),   # sounding fundamental — the octave harmonic
    (1320.0, 0.42, 0.60),  # 3f — octave+fifth, the "chime" colour
    (2200.0, 0.18, 0.95),  # 5f — major third + 2 octaves, glass
    (3080.0, 0.08, 1.30),  # 7f — the slightly flat "harmonic 7th" sparkle
    # Decay rates 0.35–1.30 are the SLOWEST of the struck/plucked set
    # (vibraphone 0.30–1.10, timpani 0.9–3.0, xylophone 9–20): one surviving
    # partial has nowhere to leak energy, so the harmonic rings for seconds.
]
MODAL_PRESET = "string"  # closest stock bank (harmonic 1-D string modes) —
                         # but it keeps the EVEN partials, which the node
                         # kills; the custom GUITAR_HARMONICS_MODES bank is
                         # the real voice.

# Karplus-Strong fallback — the string IS still plucked, so KS is a legitimate
# second engine (unlike the struck-bar instruments). The node touch damps
# every partial except one, which is why the loop is almost lossless.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9988,     # highest in the KB (harp 0.9985): a single
                             #   surviving partial decays slower than any
                             #   full-spectrum open string. Measured tail
                             #   (1–2 s) 0.00156 vs 0.00015 for a 0.990 dull
                             #   control = 10.7x, and 1.11x the harp's.
    "excitation": "harmonic", # narrow node excitation, not a full pick stroke
    "width": 0.22,           # narrow pulse — glassy, no low-order body
    "lowpass_hz": 9000,      # harmonics keep their top; only the loop filter
                             #   tames the very top
    "noise_component": 0.004, # almost no pick scrape — the touch is a finger
                              #   on the string, not a plectrum strike
    "role": "lead",
}

# Phase-mod alternative (cheap chime)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,   # octave-locked modulator keeps the spectrum odd
    "mod_depth": 0.8,        # shallow — harmonics are near-sinusoidal
    "attack": 0.002,
    "release": 0.60,         # long ring-out
}

# Production defaults
REVERB_TAIL = 2.6        # seconds — the longest guitar tail in the KB: the
                         #   chime is meant to float (ambient/ice-intro use);
                         #   pull to ~1.2 s when it must sit inside a busy mix
EQ_BODY = (240, -2.0)    # peaking cut Hz, dB — remove the little body thump
                         #   the pick transient leaves under the chime
EQ_PRESENCE = (5000, 2.0) # peaking boost Hz, dB — the 5f/7f glass band is the
                          #   identity of the sound; lift it
EQ_AIR = (10500, 2.0)    # highshelf Hz, dB — shimmer above the guitar's normal
                         #   air band (steel guitar shelf sits at 9 kHz)
PAN = -0.15              # centre-left; wide ±0.5 doubles give the classic
                         #   stereo harmonic shimmer


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion (WRITTEN pitch, no transposition)."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
