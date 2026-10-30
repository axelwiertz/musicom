# -*- coding: utf-8 -*-
"""Tango Accordion (Bandoneón) — musicom instrument constants.

GM23 = "Tango Accordion" (GM1 spec). In GM the slot exists to give the tango
repertoire its signature voice: the **bandoneón**, the bisonoric German
concertina (Heinrich Band, Krefeld ~1846) that German and Italian emigrants
carried to the Río de la Plata around 1870 and that became the melodic soul of
the orquesta típica (two bandoneones, two violins, piano, double bass, flute).

Distinct from `accordion` (GM21, piano accordion): the bandoneón is BUTTON
operated, bisonoric (a button sounds a different note on push vs pull), has no
register switches (it always uses the same reed sets), and — the timbre fact
that matters most — every note is sounded by TWO reeds tuned an OCTAVE apart.
That octave-coupled pair is why the instrument cuts through an ensemble with a
nasal, reedy, slightly hollow cry instead of the accordion's musette chorus.
The left hand sits in a wooden box (nasal, muted), the right hand is bright and
sharp.

Companion to instrument.md. Import in compositions to get MIDI program, range
zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 23
GM_NAME = "Tango Accordion"
# RenderPipeline stem label: GM_PROGRAMS[23] = "Tango Accordion" -> sanitized
# trackXX_Tango_Accordion.wav. FluidR3 preset 23 is named "Bandoneon"
# (cosmetic mismatch only — no routing impact; see instrument.md quirks).
STEM_LABEL = "Tango_Accordion"

# MIDI ranges. The physical 142-tone / 71-key Rheinische-system bandoneón
# spans nearly five octaves (de.wikipedia "fast fünf Oktaven"; fr.wikipedia
# says the tessitura "approaches six octaves" once the octave-coupled second
# voice is counted). Endpoints vary by system (142 vs 152 tones) — the band
# below is the practical written band: F2 (low left-hand reed) to C7 (top of
# the right-hand keyboard). The FluidR3 patch itself plays the full keyboard
# (empirical sweep 24–108 audible, 15/15).
RANGE_MIN = 41       # F2 — lowest left-hand (bass side) reed
RANGE_MAX = 96       # C7 — top of the right-hand (discant) keyboard
SOLO_RANGE = (53, 91)   # F3–G6 — the exposed melodic span of the patch
SWEET_SPOT = (57, 84)   # A3–C6 — the tango cantabile register: the "cry"

# Register zones (hand assignment + timbre changes across the instrument)
ZONES = {
    "bass": (41, 59),        # F2–B3 — left hand inside the wooden box: nasal,
                             #   muted, reedy; bass lines and marcato roots
    "low_mid": (60, 67),     # C4–G4 — hand-overlap zone, both keyboards can
                             #   reach it; full, woody body
    "cantabile": (68, 79),   # G#4–G5 — THE tango melody register: singing,
                             #   crying, most expressive reed tone
    "high": (80, 91),        # G#5–G6 — bright, sharp, piercing right hand;
                             #   ornament runs, counter-lines
    "top": (92, 96),         # G6–C7 — thin, squealing top of the keyboard;
                             #   use sparingly (rhetorical accents only)
}

# Articulation defaults (velocity, duration_factor)
# Names follow tango bandoneón usage where a term exists.
ARTICULATIONS = {
    "cantabile": (70, 1.0),      # singing draw-stroke line — the default
    "sustain": (76, 1.0),        # steady bellows, held note
    "marcato": (92, 0.85),       # tango accent ("acento") — hard bellows start
    "picado": (82, 0.22),        # staccato, short bellows pulse
    "fuelle": (78, 0.5),         # bellows tremolo/swell — the tango "breath"
    "lloron": (74, 1.0),         # "crying" — wide slow vibrato + bellows
                                 #   pressure, the Piazzolla slow-movement voice
    "arrastre": (86, 0.65),      # "drag" — a slide into the note (approximate
                                 #   in MIDI with a fast chromatic grace run;
                                 #   SF2 ignores portamento CCs)
    "chasquido": (96, 0.12),     # whip/click — the bellows slap percussion
                                 #   that punctuates tango phrases
    "golpe": (100, 0.08),        # tap on the instrument box — percussive
                                 #   accent (a knock, not a pitch)
    "sforzando": (98, 0.55),     # sudden forceful push then release
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth — a free
                          #   reed IS a phase-modulated oscillator; the octave-
                          #   coupled second reed is rendered as a second
                          #   PhaseModSynth voice one octave up (see
                          #   OCTAVE_DOUBLE below)
FM_DEFAULTS = {
    "carrier_shape": "saw",     # free reed = symmetric oscillator: even + odd
                                #   harmonics (oboe/sax/accordion family)
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 3.4,           # bandoneón is EDGIER than the accordion (3.2):
                                #   the metal reed sits in a shallow, hard
                                #   reed block and the octave pair adds bite;
                                #   still below bagpipe (4.5)
    "attack": 0.018,            # fast — a heavy reed speaks almost instantly
                                #   on bellows pressure (slightly slower than
                                #   the accordion's 0.015: more air mass)
    "release": 0.07,            # near-instant — the reed stops at the button
    "sustain_level": 0.82,      # bellows hold the level; little natural decay
    "octave_double": 0.45,      # THE bandoneón tell: a second reed tuned one
                                #   octave above, at ~45% amplitude (the two
                                #   reeds are "octave-coupled", not detuned)
}
SYNTHESIS_DEFAULTS = {
    "instrument": "tango_accordion",
    **FM_DEFAULTS,
}

# Additive alternative — the octave-doubled harmonic stack, explicit
ADDITIVE_DEFAULTS = {
    "harmonic_count": 10,
    # h2 (the octave reed) is unusually strong for a reed instrument
    # NOTE: unnormalized relative amplitudes — `SoundWave.apply_overtones`
    # asserts the list sums to 1.0, so normalize (w / w.sum()) at the call site.
    "harmonic_weights": [1.0, 0.55, 0.42, 0.30, 0.22, 0.14, 0.11, 0.08,
                         0.06, 0.045],
    "attack": 0.02,
    "release": 0.08,
}

MODAL_PRESET = "tube"  # modal fallback: closed-tube/reed-ish resonator
                       #   (accordion/reed_organ use "string"; "tube" keeps the
                       #   odd-harmonic hollow that reads as a reed)

# Production defaults
REVERB_TAIL = 1.8       # seconds — tango salon/hall: the cry needs air; a
                        #   dry bandoneón sounds like a toy accordion. Longer
                        #   than accordion 1.4, shorter than string_ensemble 2.6
EQ_BODY = (250, -2.0)   # peaking cut Hz, dB — tame the wooden-box boom and
                        #   the nasal left-hand resonance
EQ_PRESENCE = (3000, 2.5)  # peaking boost Hz, dB — the reed edge that makes
                           #   the bandoneón cut through the ensemble
EQ_AIR = (7500, 0.8)    # highshelf Hz, dB — gentle key/valve noise sparkle
PAN = 0.0               # center for a solo stem; ±0.2 spread when doubling
                        #   left-hand (bass) against right-hand (treble)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
