# -*- coding: utf-8 -*-
"""Woodblock — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with a custom WOODBLOCK_MODES bank. A woodblock is
a hollowed hardwood SLIT BLOCK: a struck wooden idiophone whose modes are
weakly inharmonic and die almost instantly (~60-90 ms to inaudibility). The
modal ratio set below is MEASURED from FluidR3 GM115 (1 : 1.96 : 2.18 : 3.44 :
5.5) rather than textbook: the 2.18x partial is the "wooden clack" that makes
it read as WOOD, and the 1.96x near-octave is the body "tock". Decay rates
70-260 are an order of magnitude faster than the marimba bank (8-20) — this
is the shortest ring in the percussion KB. Karplus-Strong is NOT appropriate:
no string, no tube, and a KS loop's harmonic series is the wrong structure
(the timpani / taiko / agogo precedent). Stock MODAL_PRESET 'drum' is the
closest bank (fast, inharmonic) but membrane-shaped — WOODBLOCK_MODES is the
real voice.

Identity: GM115 = woodblock — the Western orchestral/studio hardwood slit
block (maple, 5-9 in), struck with a drumstick or hard mallet. NOT the
claves (GM ch9 note 75: a solid rod, ~1080 Hz measured, a fourth+ higher),
NOT the cowbell (ch9 note 56: metal, long ring), NOT the muyu / temple block
(round fish-mouth block, no GM program), NOT the taiko (GM116: membrane).

MEASURED QUIRK (this is the important one): FluidR3 GM115 barely
pitch-tracks. Sweeping MIDI 50 -> 98 moves the spectral peak only
330 Hz -> 580 Hz (1.76x) where real transposition would be 16x. Note number
is a TIMBRE control, not a pitch control — the patch always sounds like the
same block. The sample's natural pitch is note ~68 (G#4, 410 Hz measured).
=> do NOT write melodies on GM115, and do NOT expect a high/low pair from it:
for a true hi/lo pair use channel 9 notes 76 (Hi, 380 Hz measured) and
77 (Low, 280 Hz measured) in FluidR3.
"""

MIDI_PROGRAM = 115
GM_NAME = "Woodblock"
# RenderPipeline stem label: GM_PROGRAMS[115] = "Woodblock" -> stem file
# trackXX_Woodblock.wav (matches exactly, no quirk; FluidR3 preset 115 =
# "Woodblock", bank 0 — labels match)
STEM_LABEL = "Woodblock"

# MIDI ranges. A woodblock has NO melodic range — these are the window in
# which the GM115 patch still reads as a woodblock, not a playable scale.
RANGE_MIN = 60      # C4 — below this the thinned resample reads as a dull
                    #   "clop"; the patch is audible from C3 but useless
RANGE_MAX = 96      # C7 — above this it is a bare tick with no wood body
SOLO_RANGE = (65, 84)   # F4–C6 — the practical writing window: one block
                        #   colour, ostinato home note 72 (C5, 430 Hz)
SWEET_SPOT = (67, 74)   # G4–D5 — the patch's NATURAL, unresampled centre
                        #   (measured peak 410-440 Hz; natural note ~68)

# Register zones (timbre zones, NOT pitch zones — see the pitch-tracking quirk)
ZONES = {
    "low": (60, 70),     # C4–A#4 — darkest resampling: the 8-9 in low block
                         #   colour ("low" is an illusion, but a usable one)
    "mid": (71, 79),     # B4–G5 — the natural centre: fullest wood body,
                         #   the home register for a repeated ostinato
    "high": (80, 96),    # G#5–C7 — thinner, more resampled tick: the
                         #   high-block illusion used for ornament sparkle
}

# Articulation defaults (velocity, duration_factor). Durations are SHORT by
# physics: the block's own decay is ~60-90 ms, so a longer note-off is
# inaudible. Articulation lives in velocity + stroke placement.
ARTICULATIONS = {
    "open": (92, 0.25),         # hard stick on the solid cheek — the dry
                                #   standard "tock" (the default stroke)
    "accent": (106, 0.30),      # hard downbeat, maximum crack
    "muted": (68, 0.12),        # free hand/fingers clamp the block — dead
                                #   click, body removed
    "rim": (86, 0.10),          # stick on the edge over the slit — the
                                #   sharpest, thinnest sound in the set
    "stick_click": (60, 0.08),  # shoulder of the stick laid flat and pressed
                                #   — soft "clop", no crack
    "double": (90, 0.18),       # two bounces — the signature "tock-a" pair
    "ghost": (36, 0.10),        # barely-there 16th that keeps the subdivision
                                #   audible without accenting it
    "roll": (60, 0.06),         # single-stroke re-strikes at 32nd density —
                                #   there is NO true sustain, only attacks
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "drum"     # closest stock bank (fast, inharmonic) but
                          #   membrane-shaped and far too long-ringing —
                          #   use WOODBLOCK_MODES for the real voice
# Woodblock custom modes: measured FluidR3 GM115 ratios, very fast decays.
# (freq, amp, decay) — decay is a RATE (higher = faster). 70-260 gives the
# ~70 ms tock + faint tail: ~10x faster than the marimba bank (8-20) and the
# shortest ring in the percussion KB (agogo 2.2-7.0, taiko 2.6-6.0).
WOODBLOCK_MODES = [
    (430.0, 1.00, 80.0),      # 1.00x — block body fundamental (measured
                              #   430 Hz at the natural note ~68); fast die
    (843.0, 0.48, 110.0),     # 1.96x — the near-octave "tock" that gives
                              #   the block its body
    (937.0, 0.30, 140.0),     # 2.18x — the INHARMONIC wooden clack; this
                              #   ratio is what makes it read as wood, not bar
    (1480.0, 0.16, 190.0),    # 3.44x — slit/edge crack resonance
    (2365.0, 0.10, 260.0),    # 5.50x — hard-stick tick, dies first
]

# Phase-mod alternative patch (cheap woodblock: inharmonic ratio = wood)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.4,    # non-integer = inharmonic = wooden; an integer
                              #   ratio would read as a pitched bar
    "mod_depth": 1.8,
    "attack": 0.0005,
    "release": 0.06,          # 60 ms — the block is over before the release
}

# Channel-9 alternative (true hi/lo block pair; GM percussion map)
CH9_WOODBLOCK = {
    "hi": 76,    # Hi Wood Block — 380 Hz measured in FluidR3 (low-ish!)
    "low": 77,   # Low Wood Block — 280 Hz measured (a fifth below "hi")
    "peak_at_vel_100": 0.55,   # ~4.5 dB hotter than melodic GM115 (0.34)
}

# Production defaults
REVERB_TAIL = 0.75      # seconds — the DRIEST entry in the KB. A woodblock
                        #   is close-mic'd; longer tails smear the tick into a
                        #   wood "clop" and destroy its marker function
EQ_BODY = (600, -2.0)   # peaking cut Hz, dB — the hollow-slit boxiness under
                        #   the fundamental
EQ_PRESENCE = (3600, 2.5)  # peaking boost Hz, dB — the stick crack; this is
                           #   the band that makes the block cut a mix
EQ_AIR = (10000, 1.5)   # highshelf Hz, dB — dry top; do NOT low-pass a
                        #   woodblock, the tick band IS the instrument
PAN = 0.15              # slightly right for a mix placement (standard
                        #   percussion seating); 0.0 when it is the only
                        #   percussion voice


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
