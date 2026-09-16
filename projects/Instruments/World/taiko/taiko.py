# -*- coding: utf-8 -*-
"""Taiko Drum — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with a custom TAIKO_MODES bank. A taiko head is a
large tacked/roped cowhide membrane with an inharmonic modal family (Bessel
ratios like the timpani), but with a much DENSER, harder strike (cedar bachi)
and, above all, a BODY: the hollowed keyaki-log shell resonates around
60-110 Hz and gives the drum its chest thump. TAIKO_MODES therefore couples
a tuned (0,1) head mode to inharmonic membrane partners and a low shell
mode at ~1.4x the fundamental. MODAL_PRESET 'drum' is the closest stock
bank but decays too fast and carries no shell body; DRUM606_DEFAULTS
(sound/synthesis/drum_synth_606.py, `DrumSynth606.tom` with an extended
decay) covers the pitch-swept-sine thump of the strike transient.
Karplus-Strong is NOT appropriate — there is no string.

Identity: GM116 = taiko (wadaiko), the big Japanese barrel/kokirizutsu
drum on a slanted stand — a large tacked cowhide head over a hollowed
keyaki (zelkova) shell, struck with thick cedar bachi. A ceremonial,
THEATRICAL instrument (kumi-daiko festival ensembles, kabuki/noh
accompaniment) with huge body, short ring, and sharp vertical accents.
NOT the timpani (pitched, mallets, pedal tuning); the taiko is played
kuchi-shoga rhythm syllables ("DON don DON DOKO") and lands accents on
the 1. Distinct from GM117 Melodic Tom (higher, tom-tuned for melodic
fills) — the taiko is the low, deep, festival voice of the GM drum block.
"""

MIDI_PROGRAM = 116
GM_NAME = "Taiko Drum"
# RenderPipeline stem label: GM_PROGRAMS[116] = "Taiko Drum" -> stem file
# trackXX_Taiko_Drum.wav (matches exactly, no quirk; FluidR3 preset 116 =
# "Taiko Drum" — labels match exactly)
STEM_LABEL = "Taiko Drum"

# MIDI ranges (sounding pitch; the melodic taiko patch is a tuned drum:
# pitch follows the played note, like a timpano without the pedal)
RANGE_MIN = 36      # C2 — low-chū-daiko / ō-daiko floor (real ō-daiko ~
                    #   fundamental 60-80 Hz = B1-B2 territory; below C2 the
                    #   SF2 patch thins out)
RANGE_MAX = 67      # G4 — koda/shime-daiko ceiling of the melodic patch
                    #   (smaller shime drums sit ~an octave above the chū)
SOLO_RANGE = (40, 55)   # E2–G3 — the big chū-daiko festival core: DON
                        #   strokes, kabuki ramps, kumi-daiko low ensemble
SWEET_SPOT = (45, 57)   # A2–A3 — fullest chest tone, strongest body
                        #   resonance, clearest DON punch

# Register zones
ZONES = {
    "low": (36, 45),     # C2–A2 — ō-daiko chest booms; the kumi-daiko floor
    "mid": (46, 57),     # A#2–A3 — chū-daiko festival zone: DON/DOKO,
                         #   clearest pitch + body coupling
    "high": (58, 67),    # A#3–G4 — shime/koda accents: slaps and rim cracks,
                         #   thin and dry
}

# Articulation defaults (velocity, duration_factor). Kuchi-shoga: DON =
# full fat stroke on the head center, DOKO = lighter off-beat stroke, KA =
# rim crack (wood only), SU = rest.
ARTICULATIONS = {
    "don": (96, 0.8),         # full head-center stroke — the fat festival
                              #   punch (ka the 1, let it ring)
    "doko": (74, 0.4),        # lighter off-beat stroke — galloping filler
    "ka_rim": (88, 0.15),     # rim crack (edge of head on shell) — wood
                              #   click, no tone (kuchi-shoga "KA")
    "slap": (90, 0.25),       # quick sharp head slap — bright crack accent
    "roll": (70, 0.06),       # two-stick tremolo — shime-daiko roll, the
                              #   only sustain illusion (short re-strikes)
    "muffle": (58, 0.12),     # hand-damped stroke — dead thud under the
                              #   next player's solo
    "accent": (99, 0.9),      # hard accent — downbeat qi/atare hits
    "soft": (50, 0.7),        # soft stroke — hirajoshi ensemble support at p
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "drum"     # closest stock strike-membrane bank (FAST decay,
                          #   no shell body — use TAIKO_MODES for the real
                          #   chest thump)
# Taiko custom modes: tuned circular-membrane (0,1) head mode with inharmonic
# Bessel partners, COUPLED to a low hollowed-keyaki shell resonance (~90 Hz
# at the tuned A2 reference — pitch-shift by the played note, like timpani).
# (freq, amp, decay) — decay rates are MODERATE (a taiko ring is ~0.5-0.8 s,
# much shorter than timpani's 0.9-3.0 but longer than a tuned 606 tom):
TAIKO_MODES = [
    (90.0, 1.00, 2.6),     # shell mode ~90 Hz — the chest/body thump,
                           #   the taiko's signature (bigger than the head's
                           #   tuned fundamental in perceived loudness)
    (110.0, 0.70, 2.8),    # head (0,1) — the tuned pitch (A2 reference)
    (176.0, 0.35, 3.5),    # 1.6x (1,1) membrane partner — hollow body band
    (234.0, 0.22, 4.5),    # 2.14x (2,1) membrane partner — strike color
    (290.0, 0.12, 6.0),    # ~2.65x (3,1) — bright edge of the strike
]

# DrumSynth606 alternative (pitch-swept sine = the strike thump)
DRUM606_DEFAULTS = {
    "freq": 80.0,          # sweep bottom — below the 606 tom's 110: taiko
                           #   chest is lower and fatter
    "decay": 1.4,          # much longer than the 606 tom (0.3): big drum,
                           #   big ring — but still far below timpani 2.2+
    "pitch_sweep": 1.45,   # harder head-tension drop than timpani: the
                           #   bachi lands HARD on a loose tacked head
}

# Phase-mod alternative patch (cheap taiko thump)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.59,   # the (1,1) membrane partner
    "mod_depth": 1.0,
    "attack": 0.001,
    "release": 0.8,
}

# Production defaults
REVERB_TAIL = 1.6       # seconds — kumi-daiko plays in festival halls and
                        #   outdoors; keep some air but don't smear the DON
                        #   (timpani 2.2 hall vs xylophone 0.9 tight room)
EQ_BODY = (300, -1.5)   # peaking cut Hz, dB — tame box/shell honk above the
                        #   chest band, keep the 60-110 Hz thump intact
EQ_PRESENCE = (1800, 2.0)  # peaking boost Hz, dB — cedar-bachi head-slap
                           #   attack point (lower than mallet bars: raw hide)
EQ_AIR = (6000, 0.5)    # highshelf Hz, dB — very subtle; leather head noise,
                        #   no cymbal-like air
PAN = 0.0               # center for solo; kumi-daiko arcs spread
                        #   -0.3..+0.3 with the ō-daiko slightly left


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
