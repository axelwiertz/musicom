# -*- coding: utf-8 -*-
"""Agogo — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is ModalSynth
(sound/synthesis/modal.py) with a custom AGOGO_MODES bank. An agogo bell is
a forged/sheet-metal struck idiophone: a damped-sinusoid resonator bank is
the exact physical model (no string, no membrane). The bell is much more
TUNED than a church bell — a strong fundamental, an octave-ish second
partial and a short inharmonic tail — and it rings for roughly a second,
so the decay rates sit LOW (2.2-7.0, i.e. a long-ish ring) between the
vibraphone (0.30-1.10) and the taiko (2.6-6.0). MODAL_PRESET 'bell' is the
closest stock bank but is a WESTERN CAST BELL (minor-third tierce, long
slow tail) — wrong for a thin forged agogo; the custom AGOGO_MODES is the
real voice. Karplus-Strong is NOT appropriate: there is no string, and a
KS loop's harmonic series is the wrong partial structure (the timpani /
taiko precedent).

Identity: GM113 = agogo — the Yoruba-derived multiple hand-bell of
West Africa, carried to Brazil through the slave trade and now the
TIMEKEEPER of samba (bateria), samba de roda, batucada, capoeira and
candomble. Two (sometimes three or four) conical sheet-metal bells of
different pitch are welded to a curved metal handle and struck with a
wooden or metal stick; the two-bell set is tuned roughly a third to a
fourth apart and the player alternates between them to play a fixed
cyclic TIMELINE pattern — the Brazilian cousin of the Afro-Cuban clave.
NOT the cowbell (GM 22 territory / a single square bell), NOT the
woodblock (GM115, hollow wooden slit), NOT the triange: the agogo's
identity is the PAIR of pitched metal bells and the alternating
timeline figure.
"""

MIDI_PROGRAM = 113
GM_NAME = "Agogo"
# RenderPipeline stem label: GM_PROGRAMS[113] = "Agogo" -> stem file
# trackXX_Agogo.wav (matches exactly, no quirk; FluidR3 preset 113 =
# "Agogo" — labels match exactly)
STEM_LABEL = "Agogo"

# MIDI ranges (sounding pitch; the GM agogo patch is pitched — every note
# plays a bell tone, so the composer can write the pair as two pitches)
RANGE_MIN = 55      # G3 — low-bell floor; below G3 the sheet-metal patch
                    #   loses its pitch centre and reads as a dull clank
RANGE_MAX = 96      # C7 — small-bell (agogo-mirim) ceiling; the GM patch
                    #   plays higher but the metal turns to a thin tick
SOLO_RANGE = (67, 84)   # G4–C6 — the REAL two-bell pair: low bell ~A4–C5,
                        #   high bell ~D5–G5 (a third to a fourth apart),
                        #   plus the small third bell of a 3-bell set
SWEET_SPOT = (69, 81)   # A4–A5 — fullest metal tone: the low bell at A4
                        #   and the high bell a fourth up at D5

# Register zones
ZONES = {
    "low": (55, 66),     # G3–F#4 — large low bell (agogo grande / the
                         #   candomble gã): fat bronze ring, slower decay
    "mid": (67, 79),     # G4–G5 — the standard samba pair: low bell +
                         #   high bell, the timeline octave-third core
    "high": (80, 96),    # G#5–C7 — small bell (agogo-mirim): thin bright
                         #   tick, 3-4 bell sets and ornament sparkle
}

# Articulation defaults (velocity, duration_factor). The agogo is played
# with ONE stick, so the two bells are struck alternately, not together.
ARTICULATIONS = {
    "open_high": (96, 0.6),      # stick on the HIGH bell, free ring — the
                                 #   "teleco" of the samba timeline
    "open_low": (92, 0.8),       # stick on the LOW bell — fatter, longer
                                 #   ring; the downbeat "tá"
    "alternating": (84, 0.5),    # the timeline itself: high/low
                                 #   alternation in 16ths (the clave figure)
    "muted": (70, 0.15),         # free hand clamps the bell (or stick on
                                 #   the bell body) — dead click, no ring
    "rim": (88, 0.10),           # strike on the rim/edge — metallic tick,
                                 #   the sharpest sound in the set
    "double": (94, 0.35),        # two quick strokes (stick bounce) — the
                                 #   flam that pushes a samba virada
    "ghost": (40, 0.12),         # barely-there ghost 16th — keeps the
                                 #   timeline flowing without accenting
    "accent": (104, 0.55),       # hard downbeat accent — the batucada
                                 #   "1" that the whole bateria locks to
    "roll": (66, 0.08),          # fast single-stick tremolo on one bell —
                                 #   the only sustain illusion (re-strikes)
}

# Synthesis engine recommendation
SYNTHESIS = "modal"       # sound/synthesis/modal.py ModalSynth
MODAL_PRESET = "bell"     # closest stock bank (inharmonic metal), but a
                          #   CAST WESTERN BELL (minor-3rd tierce, very long
                          #   tail) — use AGOGO_MODES for the real voice
# Agogo custom modes: forged sheet-metal bell, tuned fundamental + near-
# octave partner + short inharmonic tail. (freq, amp, decay) — decay is a
# RATE (higher = faster); 2.2-7.0 gives the ~1 s agogo ring, LOWer than the
# marimba (8-20) and close to the taiko (2.6-6.0) but BRIGHTER.
AGOGO_MODES = [
    (440.0, 1.00, 2.2),     # fundamental (A4 reference) — the bell's pitch,
                            #   long ring; this is what the pair is tuned to
    (880.0, 0.42, 3.4),     # ~2x — the strong near-octave partner that
                            #   gives the agogo its "two-tone" clarity
    (1195.0, 0.22, 4.8),    # ~2.72x — inharmonic metal partial (the
                            #   classic struck-bell 2.7 ratio), attack color
    (1790.0, 0.12, 6.2),    # ~4.07x — bright rim shimmer
    (2380.0, 0.06, 7.0),    # ~5.4x — top sparkle, dies first
]

# Phase-mod alternative patch (cheap bell: inharmonic FM is the classic
# bell recipe)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.72,   # the inharmonic metal ratio — NOT an integer
    "mod_depth": 2.4,
    "attack": 0.001,
    "release": 0.9,
}

# Production defaults
REVERB_TAIL = 1.3       # seconds — samba is a STREET/roda instrument: the
                        #   bell is dry and cutting, it must poke through a
                        #   whole bateria (shorter than the taiko 1.6)
EQ_BODY = (420, -1.5)   # peaking cut Hz, dB — tame the boxy low-mid under
                        #   the bell's fundamental; keep the metal ring
EQ_PRESENCE = (3200, 2.5)  # peaking boost Hz, dB — the stick-on-metal
                           #   clank, the sound that cuts through drums
EQ_AIR = (9000, 1.0)    # highshelf Hz, dB — sheet-metal shimmer (bells
                        #   carry real top end, unlike hide drums)
PAN = 0.0               # center for solo; in a bateria spread the agogo
                        #   slightly right (+0.15) opposite the tamborim


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
