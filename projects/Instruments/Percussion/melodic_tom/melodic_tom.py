# -*- coding: utf-8 -*-
"""Melodic Tom — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with a custom MELODIC_TOM_MODES bank. A melodic
tom is a SINGLE-HEADED drum (concert tom / rototom) tuned to a pitch — the
same circular-membrane physics as the timpani and taiko (inharmonic Bessel
partial family), but a SMALLER drum: shorter ring, brighter attack, higher
tuning. Decay rates sit between timpani (0.9–3.0) and marimba (8–20).
MODAL_PRESET 'drum' is the closest stock bank (fast, inharmonic) but carries
no tuned-head fundamental. DRUM606_DEFAULTS
(sound/synthesis/drum_synth_606.py, `DrumSynth606.tom`) covers the
pitch-swept-sine strike thump. Karplus-Strong is NOT appropriate — there is
no string (the timpani/taiko precedent).

Identity: GM117 = Melodic Tom — the tuned tom-tom set of the GM percussion
block, the 70s/80s "melodic tom fill" voice (Toto "Africa" intro, Men at
Work "Down Under", The Police "Every Breath You Take", Phil Collins
"In the Air Tonight" gated toms). A set of single-headed concert
toms/rototoms tuned in scale steps, played as FILLS and drum breaks — NOT a
chromatic melodic instrument. Distinct from GM116 Taiko (low deep festival
drum), GM47 Timpani (pedal-tuned kettledrums, mallets).

Measured FluidR3/TimGM6mb behavior (2026-11-16): the patch is a LOW-FIDELITY
tuned-drum sample — the dominant partial stays in the 50–95 Hz band (rising
only ~1 octave of pitch across 4 octaves of notes; spectral centroid creeps
1.1→1.5 kHz). Note number is a COARSE timbre/pitch control, NOT a chromatic
transposition — never write chromatic runs (the woodblock lesson: note
number ≠ melody). See instrument.md for the full quirk list, including the
pipeline-wide "every 2nd note-on renders quiet" artifact shared by all
decaying patches (timpani/taiko/woodblock/piano/bass).
"""

MIDI_PROGRAM = 117
GM_NAME = "Melodic Tom"
# RenderPipeline stem label: GM_PROGRAMS[117] = "Melodic Tom" -> stem file
# trackXX_Melodic_Tom.wav (matches exactly, no quirk; FluidR3 preset 117 =
# "Melodic Tom" — labels match exactly)
STEM_LABEL = "Melodic Tom"

# MIDI ranges (sounding pitch; the patch is a tuned drum — pitch follows the
# played note only COARSELY, see module docstring)
RANGE_MIN = 36      # C2 — floor-tom register of the patch (isolated notes
                    #   audible 30–108; 36 is the real floor-tom floor)
RANGE_MAX = 96      # C6 — rototom ceiling of the patch span
SOLO_RANGE = (48, 72)   # C3–C5 — the classic 70s/80s fill register (Toto
                        #   Africa intro sits ~57–64; Men at Work toms ~55–62)
SWEET_SPOT = (52, 67)   # E3–G4 — fullest thump + clearest attack balance

# Register zones
ZONES = {
    "low": (36, 47),     # C2–B2 — floor toms: chest thump, the fill "root"
    "mid": (48, 60),     # C3–C4 — the classic melodic-fill register: clearest
                         #   pitch + body coupling (sweet-spot core)
    "high": (61, 96),    # C#4–C6 — rack toms/rototoms: thin, bright, dry
}

# Articulation defaults (velocity, duration_factor). Fills on a tuned tom
# set: stick strokes graded by intensity; the ring IS the sustain (no
# dampers on concert toms — the player muffles by hand for the next stroke).
ARTICULATIONS = {
    "fill_16": (96, 0.35),    # 16th-note fill stroke — the standard fill unit
    "fill_8": (104, 0.5),     # 8th-note fill stroke — bigger, more ring
    "accent": (112, 0.6),     # downbeat accent — the fill's landing note
    "ghost": (40, 0.2),       # ghost tap — texture between the loud hits
    "rim": (88, 0.12),        # rim shot — crack on the hoop, no tone
    "roll": (80, 0.1),        # buzz roll — the only sustain illusion
    "flam": (92, 0.15),       # flam — grace stroke + main stroke
    "soft": (60, 0.5),        # soft stroke — verse fills at p
    "toms_together": (100, 0.4),  # double-stop (two toms) — bigger fill hit
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "drum"     # closest stock strike-membrane bank (FAST decay,
                          #   no tuned-head fundamental — use
                          #   MELODIC_TOM_MODES for the real tom)
# Melodic tom custom modes: tuned circular-membrane (0,1) head mode with
# inharmonic Bessel partners (the timpani/taiko family) at a HIGHER
# reference (F3 = 174 Hz — the mid-fill register; pitch-shift by the played
# note, like timpani/taiko). Decay rates are MODERATE — a concert tom rings
# ~0.5–1.0 s (measured FluidR3: −90% in ~0.3–0.5 s, tail to ~1 s): faster
# than timpani (0.9–3.0), slower than the marimba bank (8–20):
MELODIC_TOM_MODES = [
    (174.0, 1.00, 4.5),     # head (0,1) — the tuned fundamental (F3 ref)
    (277.0, 0.55, 5.5),     # 1.59x (1,1) membrane partner — hollow body band
    (372.0, 0.32, 6.5),     # 2.14x (2,1) partner — strike color
    (483.0, 0.18, 8.0),     # ~2.78x — bright edge of the stick attack
    (620.0, 0.10, 9.5),     # ~3.56x — the crack
]

# DrumSynth606 alternative (pitch-swept sine = the strike thump)
DRUM606_DEFAULTS = {
    "freq": 174.0,          # F3 — the tom speaks HIGHER than the taiko's 80
                            #   Hz (smaller drum, tighter head)
    "decay": 0.8,           # longer than the 606 tom (0.3): a concert tom
                            #   rings — but far below timpani 2.2+
    "pitch_sweep": 1.25,    # moderate head-tension drop (stick on tuned head)
}

# Phase-mod alternative patch (cheap tom thump)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.59,   # the (1,1) membrane partner
    "mod_depth": 1.2,
    "attack": 0.001,
    "release": 0.5,
}

# Production defaults
REVERB_TAIL = 1.2       # seconds — pop/rock drum room: long enough for the
                        #   fill to bloom, short enough to keep 16th clarity
                        #   (taiko 1.6 festival hall vs woodblock 0.75 dry)
EQ_BODY = (280, -2.0)   # peaking cut Hz, dB — tame box/shell honk above the
                        #   chest band, keep the thump intact
EQ_PRESENCE = (2400, 2.0)  # peaking boost Hz, dB — drumstick-on-head attack
                           #   point (between taiko's 1.8k raw hide and
                           #   woodblock's 3.6k stick crack)
EQ_AIR = (7000, 0.8)    # highshelf Hz, dB — subtle; stick/head noise, no
                        #   cymbal shimmer
PAN = 0.0               # center for a solo fill; kit spreads toms
                        #   -0.3..+0.3 (floor right, rack left)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
