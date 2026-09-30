# -*- coding: utf-8 -*-
"""Clavinet (Hohner Clavinet D6) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM7 Clavi — the rubber-hammer struck-string electric clavichord
invented by Ernst Zacharias for Hohner (1964). The funkiest keyboard ever:
Stevie Wonder "Superstition", Billy Preston "Outa-Space", Herbie Hancock
"Chameleon".

Synthesis note: the primary recommendation is Karplus-Strong (struck
waveguide — sound/synthesis/karplus_strong.py). The clavinet is a
RUBBER-TIPPED hammer striking a steel string with a rubber mute at the
bridge — the exact physical model is a struck waveguide with high damping.
loop_gain 0.9960 is the SHORTEST in the plucked/struck KB set (harpsichord
0.9980, harp 0.9985, sitar 0.9975): the rubber mute kills energy fast.

Range is the standard 60-key Hohner Clavinet D6: F1-F6 (MIDI 29-89),
the same compass as the harpsichord but on a different principle.

The KEY timbre fact: the rubber mute at the bridge is the clavinet's
identity. It selectively damps high harmonics, creates the percussive
"cluck" at note onset, and produces the dry, midrange-focused "honk"
that cuts through a funk mix. Unlike a harpsichord or piano, the impact
velocity does NOT change loudness (rubber hammer = fixed displacement);
dynamics come from signal processing (wah, envelope filter, amp), not
from the key strike.

Composition jobs should write rhythm-section chord chops (C3-C5, the
guitar register) with staccato/sharp articulations and keep velocities
in a narrow band (75-90). Wah pedal simulation (auto-wah / envelope
filter) is the idiomatic sound.

The ModalSynth 'string' preset is the fallback (harmonic stack, fast
decay). PhaseModSynth gives a passable FM electric piano substitute.
"""
import sys

MIDI_PROGRAM = 7
GM_NAME = "Clavi"
# RenderPipeline stem label: GM_PROGRAMS[7] = "Clavi" -> stem file
# trackXX_Clavi.wav (label is "Clavi" vs FluidR3 preset "Clavinet" —
# cosmetic expansion only, no routing impact; STEM_LABEL matches the
# pipeline's real GM_PROGRAMS label so stem-file lookups work)
STEM_LABEL = "Clavi"

# MIDI ranges (sounding pitch; non-transposing, written at concert pitch)
RANGE_MIN = 29      # F1 — lowest key of the standard 60-key Clavinet D6
RANGE_MAX = 89      # F6 — highest key of the 60-key compass
SOLO_RANGE = (29, 89)  # the full 60-key span is playable solo
SWEET_SPOT = (48, 72)  # C3-C5 — the funky rhythm guitar register; the
                       #   iconic clavinet voice (Superstition riff lives
                       #   around E4-G4 / 64-67)

# Register zones
ZONES = {
    "low": (29, 47),     # F1-B2 — thumpy rubber bass zone: percussive,
                         #   thick, the funk bass line register
    "mid": (48, 72),     # C3-C5 — sweet spot: the funky rhythm guitar
                         #   register, midrange honk cuts through mix
    "high": (73, 89),    # C#5-F6 — bright clucky treble: thin, nasal,
                         #   the "wah pedal lead" register
}

# Articulation defaults (velocity, duration_factor).
# NOTE the velocity band is a CREATIVE AFFORDANCE — real clavinet has
# NO velocity sensitivity (rubber hammer = fixed strike force). Velocity
# here is mapped to articulation feel: pluck/chord = mid velocity for
# the "Superstition" chop; accent = brighter attack noise; soft = gentle
# touch. Real expression comes from the signal chain, not the keyboard.
ARTICULATIONS = {
    "pluck": (80, 1.0),        # standard rubber-hammer strike — neutral clavinet
    "chord_chop": (88, 0.7),   # funk chord stab — the "Superstition" choppy rhythm
    "hard": (100, 0.8),        # accented strike — brighter attack, more string noise
    "soft": (62, 1.0),         # gentle touch — rounder, less percussive
    "staccato": (76, 0.2),     # short percussive note — tight funk cut
    "muted": (68, 0.4),        # hand-damped / felt mute — nasal, choked
    "accent": (96, 0.9),       # sforzando marcato — brighter, louder
    "wah": (84, 0.6),          # wah-pedal note — velocity stands in for
                               #   filter position; signal chain does the rest
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"    # sound/synthesis/karplus_strong.py (SP-011)
MODAL_PRESET = "string"  # closest STOCK bank (harmonic stack, fast
                         #   decay) — the "clean struck string" fallback

# Karplus-Strong primary: struck waveguide with rubber mute damping.
# loop_gain 0.9960 — SHORTEST in the plucked/struck KB set (harpsichord
# 0.9980, harp 0.9985, sitar 0.9975, banjo 0.9960): the rubber mute at
# the bridge kills energy ~2-3x faster than the harpsichord's cloth
# damper and much faster than the harp's undamped strings.
# The noise_component (0.03) models the rubber "cluck" at note onset,
# the clavinet's signature percussive attack.
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,    # shortest in the plucked set — rubber mute
                            #   kills energy fast: ~0.3-1.5 s ring
    "noise_component": 0.03,  # rubber "cluck" at onset — the signature
                              #   clavinet attack noise; higher than any
                              #   other KS instrument in the KB
    "width": 0.3,           # focused, mono-like stereo — the clavinet is
                            #   a compact keyboard, not a spread piano
    "role": "rhythm",
}

# Modal custom bank for the mid-register rubber-hammer strike (A4
# reference): a near-harmonic struck-string stack with FAST decay.
# decay is a RATE (higher = faster), so these are MUCH higher than
# the harpsichord's 0.35-0.90 — the rubber mute kills energy fast.
# The noise_onset models the rubber "cluck".
CLAVI_MODES = [
    (440.0, 1.00, 6.0),     # f0 (A4) — struck string fundamental, 0.5-1.0 s ring
    (880.0, 0.65, 8.0),     # 2x — octave, strong (the guitar-like twang)
    (1320.0, 0.45, 12.0),   # 3x — twelfth, the midrange "honk"
    (1760.0, 0.25, 16.0),   # 4x — double octave, bright transient
    (2200.0, 0.15, 20.0),   # 5x — treble ring, fast decay
    (2640.0, 0.08, 25.0),   # 6x — highest partial, dies fast
]

# Phase-mod alternative patch (FM electric piano — thinner but usable)
FM_DEFAULTS = {
    "carrier_shape": "saw",     # saw = richer harmonic content (string-like)
    "mod_freq_ratio": 2.0,      # the strong octave partial
    "mod_depth": 1.5,           # moderate FM — between harpsichord 2.2 and
                                #   harp 1.3; the rubber mute reduces upper
                                #   harmonics compared to a clean string
    "attack": 0.002,            # rubber hammer = near-instant string contact
    "release": 0.3,             # rubber mute stops the string fast
}

# Production defaults
REVERB_TAIL = 1.0       # seconds — short room/plate: the clavinet is a
                        #   DRY instrument; too much reverb washes out the
                        #   percussive attack and makes it sound like a
                        #   generic electric piano. 1.0 s gives the "wooden
                        #   box" acoustic space.
EQ_BODY = (400, -2.5)   # peaking cut Hz, dB — reduce boxy body resonance
                        #   (the hollow clavinet case is ~5 mm plywood)
EQ_PRESENCE = (2500, 3.0)  # peaking boost Hz, dB — the midrange "honk"
                           #   that cuts through a funk mix; the clavinet's
                           #   main identity zone (1-3 kHz)
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — subtle string shimmer; the
                        #   rubber mute naturally rolls off above 6 kHz,
                        #   so excessive air boost sounds artificial
PAN = 0.0               # center solo; sit in the keyboard/guitar zone
                        #   of a funk mix (L 20-30 for a section placement)


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)