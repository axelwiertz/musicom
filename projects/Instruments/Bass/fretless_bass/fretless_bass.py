# -*- coding: utf-8 -*-
"""Fretless Bass — musicom instrument constants.

GM35 = Fretless Bass (GM1 spec; Roland GS "Fretless Bass", Yamaha XG
"FretlessBass"). A solidbody electric bass with the frets removed and the
fingerboard filled/sanded smooth, so pitch is set by finger POSITION, not a
fret crown. Result: continuous portamento ("slide"), a nasal vocal "mwah"
midrange from the softer fingerboard contact, and no fretwire click on the
attack. Iconic players: Jaco Pastorius, Pino Palladino, Mick Karn, Sting,
Tony Franklin, Gary Willis.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.
"""

MIDI_PROGRAM = 35
GM_NAME = "Fretless Bass"
# RenderPipeline stem label: GM_PROGRAMS[35] = "Fretless Bass" -> sanitized
# trackXX_Fretless_Bass.wav (FluidR3 preset 35 = "Fretless Bass" — match)
STEM_LABEL = "Fretless_Bass"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — GM patch floor; 5-string low B0 (MIDI 23) sits
                     #   one semitone below and is reachable
RANGE_MAX = 72       # C5 — practical ceiling: above here the patch turns
                     #   nasal and loses fundamental (not idiomatic)
SOLO_RANGE = (28, 60)   # E1–C4 — melodic bass lines; the fingerboard pocket
                        #   where a fretless sings without mud
SWEET_SPOT = (33, 55)   # A1–G3 — four-string pocket: root-fifth lines,
                        #   slides, the "mwah" midrange at full body

# Register zones
ZONES = {
    "sub": (24, 35),       # C1–B1 — open E1 (28) / 5-string B0 (23):
                           #   fundamental weight, chest thump, single notes
    "groove": (36, 50),    # C2–D3 — primary rhythm register: root-fifth
                           #   support, walking bass, slide approach notes
    "singing_mid": (51, 62),  # D#3–D4 — the "mwah" zone: long glissandi,
                           #   vibrato, melodic fills, countermelody
    "upper": (63, 72),     # D#4–C5 — thumb-position upper register: thin,
                           #   cello-like, exposed solos only
}

# Articulation defaults (velocity, duration_factor)
# Fretless vocabulary is defined by PITCH CONNECTION (slides, portamento) and
# by the absence of fret click — duration factors stay long by default.
ARTICULATIONS = {
    "sustain": (70, 1.0),        # round fingerboard pluck, long ringing note
    "staccato": (76, 0.30),      # palm/fingerboard damping — tight, dry
    "slide": (72, 1.05),         # the signature glissando between two pitches
    "portamento": (64, 1.0),     # continuous bend into the target note —
                                 #   fretless-only, write as pitch-bend or a
                                 #   fast chromatic run on GM patches
    "vibrato": (76, 0.90),       # finger-roll vibrato, 5–6 Hz, widens on
                                 #   long notes
    "harmonic": (62, 1.0),       # natural harmonic at 12th/7th/5th position —
                                 #   bell-like, 1 octave up (touch nodes)
    "double_stop": (80, 0.70),   # two adjacent strings (third/sixth) —
                                 #   thumb position, not a chord
    "ghost": (36, 0.12),         # dead-note fingerboard tap — groove filler,
                                 #   no pitch
    "arco": (70, 1.0),           # bowed with a double-bass bow — sustained,
                                 #   reedy, cello-like
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"     # sound/synthesis/karplus_strong.py (SP-011)
                          # A plucked string waveguide is the physical model:
                          # the loop low-pass IS the fingerboard damping, a
                          # long loop_gain gives the fretless ring.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,   # longer sustain than the fretted electric bass
                           #   (0.9970) — the bare fingerboard damps the top
                           #   of the string less than a fret crown does
    "lowpass_hz": 2200.0,  # darker than the fretted bass: the soft
                           #   fingerboard stop rolls off the upper partials
                           #   into the nasal "mwah" band
    "width": 0.55,         # moderate stereo spread — DI bass is mono; a
                           #   little width in the harmonic tail
    "excitation": "pluck",
    "role": "bass",
}

# BowedString is the ARCO-only engine (stick–slip excitation, slow attack,
# cello-like formant) — not the default voice.
BOWED_DEFAULTS = {
    "bow_velocity": 0.18,     # slow, sustained bow stroke
    "bow_force": 1.4,         # moderate pressure — reedy, not crushed
    "bow_position": 0.18,     # sul tasto-ish: round, vocal, few high partials
    "lpf_coef": 0.6,          # waveguide low-pass: dark, cello-like
    "friction_decay": 5.0,
    "attack": 0.16,           # slow bow bite, not a pluck transient
    "release": 0.22,
    "vibrato_rate": 5.4,
    "vibrato_depth": 0.004,   # cents-scale finger vibrato
    "role": "bass",
}

# ModalSynth is a weak fallback only (harmonic stack, no pickup colour)
MODAL_PRESET = "string"

# Phase-mod alternative (cheap synth-bass approximation, not recommended —
# useful only when a purely synthetic fretless colour is wanted)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.4,         # gentle — enough to thicken, not to buzz
    "attack": 0.012,          # soft fingerboard attack (no fret click)
    "release": 0.30,
}

# Production defaults
REVERB_TAIL = 1.6        # seconds, room/plate — slightly longer than the
                         # fretted bass: the vocal quality wants air, but
                         # verb is a mix choice, never baked into the DI
EQ_BODY = (250, -2.5)    # peaking cut Hz, dB — low-mid box resonance
EQ_PRESENCE = (800, 3.0) # peaking boost Hz, dB — THE "mwah" formant; the
                         # single most important fretless EQ move
EQ_AIR = (5000, 1.5)     # highshelf Hz, dB — fingerboard squeak and string
                         # detail (fretless has no fret click to add it)
PAN = 0.0                # center — bass is universally mono/centered


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
