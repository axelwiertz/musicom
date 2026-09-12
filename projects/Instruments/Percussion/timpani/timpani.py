# -*- coding: utf-8 -*-
"""Timpani — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth (impulse-excited
resonator bank — a kettledrum head is a struck membrane, sound/synthesis/
modal.py). A timpani is NOT a harmonic resonator like a bar or a string: an
ideal circular membrane's partials follow the Bessel-zero ratios
1 : 1.594 : 2.136 : 2.296 : 2.653 (inharmonic), and the real instrument's
copper bowl + air loading pull them slightly toward the ear-pleasing set
1 : ~1.5 : ~2.1 : ~2.3 : ~2.65 — the timpani's signature "definite but
hollow" pitch, and the reason a timpano stays identifiable at any tuning.
TIMPANI_MODES below is that custom bank (tuned at A4=440 by convention;
pitch-shift the mode frequencies by the played note). MODAL_PRESET 'drum'
is the closest stock bank (low inharmonic modes, but FAST decay — wrong
envelope for timpani, which are the longest-ringing drums in the orchestra).
DRUM606_DEFAULTS (sound/synthesis/drum_synth_606.py, `DrumSynth606.tom`)
covers the pitch-swept-sine thump of the strike transient. Karplus-Strong
is NOT appropriate — there is no string.

Quirk: timpani are pitched and MUST use a melodic channel (0-9) with
program 47. Routing them to channel 9 (GM percussion) would replace the
tuned sound with the drum-kit mapping AND mislabel the stem
"Acoustic_Grand_Piano" (program-0 fallback).
"""

MIDI_PROGRAM = 47
GM_NAME = "Timpani"
# RenderPipeline stem label: GM_PROGRAMS[47] = "Timpani" -> stem file
# trackXX_Timpani.wav (matches exactly, no quirk; FluidR3 preset 47 =
# "Timpani")
STEM_LABEL = "Timpani"

# MIDI ranges (sounding pitch; standard 4-drum set + 32" low drum)
RANGE_MIN = 36      # C2 — 32-inch drum bottom (standard set bottoms at D2=38)
RANGE_MAX = 65      # F4 — extended/piccolo-timpano ceiling (Milhaud's
                    #   La création du monde asks F#4=66)
SOLO_RANGE = (38, 57)   # D2–A3 — the standard four-drum set (32/29/26/23in);
                        #   "a great majority of the orchestral repertoire
                        #   can be played using these four drums"
SWEET_SPOT = (41, 55)   # F2–G3 — fullest tone, clearest pitch, best roll
                        #   projection; each drum's own range is a 5th

# Register zones
ZONES = {
    "low": (36, 47),     # C2–B2, 32-inch/29-inch booms — deep, slow roll rumble
    "mid": (48, 57),     # C3–A3, 26-inch/23-inch drums — the classic
                         #   tuning/roll/melodic zone
    "high": (58, 65),    # B3–F4, piccolo timpano — thin, hollow, dry;
                         #   effects and Rite of Spring-style accents
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "stroke": (84, 1.0),      # standard felt-mallet stroke — long natural ring
    "roll": (72, 0.06),       # two-stick tremolo — repeated 32nds (sustain illusion)
    "muffle": (60, 0.15),     # hand damping — short, dead, no ring
    "accent": (98, 0.9),      # hard marcato stroke — sforzando downbeat
    "soft": (52, 1.0),        # piano stroke / soft beguiling roll at pp
    "edge": (70, 0.6),        # struck near the rim — thin, hollow (Bartók/Bernstein)
    "center": (78, 0.5),      # struck at the center — near-toneless thud (Gershwin)
    "double_stop": (88, 0.9), # two drums struck together (Beethoven 9, Brahms)
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "drum"     # closest stock strike-membrane bank (FAST decay —
                          #   use TIMPANI_MODES for the true long ring)
# Exact timpani custom modes: ideal circular-membrane Bessel ratios, pulled
# slightly toward 1 : 1.5 : 2.1 : 2.3 : 2.65 by bowl + air coupling.
# (freq, amp, decay) — decay rates are LOW (slow) vs marimba's 8-20: a
# timpano out-rings every other drum in the orchestra.
TIMPANI_MODES = [
    (440.0, 1.00, 0.9),    # f0 (0,1) mode — the tuned pitch
    (699.6, 0.50, 1.3),    # 1.59x (1,1) — strongest inharmonic partial
    (941.6, 0.28, 1.8),    # 2.14x (2,1) — the "hollow" band
    (1012.0, 0.18, 2.4),   # 2.30x (0,2) — axial mode, whacks the thump
    (1166.0, 0.10, 3.0),   # 2.65x (3,1) — bright strike edge
]

# DrumSynth606 alternative (pitch-swept sine = the strike thump)
DRUM606_DEFAULTS = {
    "freq": 110.0,        # sweep bottom (near the 26-inch drum's A2/A3 feel)
    "decay": 0.9,          # longer than the 606 default tom (0.3) — big drum body
    "pitch_sweep": 1.35,   # head tension drop right after the stroke
}

# Phase-mod alternative patch (cheap timpani thump)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.59,  # the (1,1) membrane partial
    "mod_depth": 1.2,
    "attack": 0.001,
    "release": 1.5,
}

# Production defaults
REVERB_TAIL = 2.2       # seconds, hall — the longest of the instrument set;
                        #   timpani ring in the room (marimba 1.0 / steel 1.4)
EQ_BODY = (200, -2.0)   # peaking cut Hz, dB — tame copper-bowl boom mud
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — felt-mallet attack point
EQ_AIR = (6500, 1.0)    # highshelf Hz, dB — subtle hall air on the head noise
PAN = 0.0               # center (a lone timpano); -0.3..+0.3 across a 4-drum
                        #   arc, low drum left (American setup)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
