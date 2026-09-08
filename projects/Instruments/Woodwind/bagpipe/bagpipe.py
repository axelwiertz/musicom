# -*- coding: utf-8 -*-
"""Bagpipe — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity note: GM109 is the generic "Bagpipe" — in the FluidR3 GM set it
renders as the Great Highland Bagpipe (GHB): a sustained double-reed
chanter (9 notes, A3-A4 written range = A4-A5 sounding, mixolydian on D)
over a constant A2 (110 Hz) drone. The GHB is a monophonic melody-over-
drone instrument — the chanter plays ONE note at a time over an UNBROKEN
drone. Composition jobs should write scale/modal melody lines over a pedal
(drone) bass, NEVER dense harmony. The signature "skirl" is an
ornament-heavy attack (gracenotes, doubling) at ~65-75 ms.

Synthesis note: the primary recommendation is PhaseModSynth (a reed is a
self-sustained oscillator driven by airflow — phase-mod of a saw/saw
carrier reproduces the chanter's strong even+odd harmonic reed spectrum,
like oboe/sax but with a HIGHER mod_depth for the bagpipe's piercing
presence and a LOW attack to simulate the reeds being already blown —
the envelope is a bag-pressure swell, not a reed transient). ModalSynth
preset 'string' (slow-decay harmonic stack) is a crude continuous-tone
fallback; there is no native chanter+drone two-part model in musicom yet.
"""

MIDI_PROGRAM = 109
GM_NAME = "Bagpipe"
# RenderPipeline stem label: GM_PROGRAMS[109] = "Bag pipe" -> stem file
# trackXX_Bag_pipe.wav. STEM_LABEL matches the pipeline's ACTUAL label
# ("Bag pipe" with a space, not "Bagpipe") so stem-file lookups work.
# FluidR3 preset 109 = "BagPipe" — cosmetic difference only.
STEM_LABEL = "Bag_pipe"

# MIDI ranges (Great Highland Bagpipe, sounding pitch)
# The GHB chanter itself sounds only A3 (MIDI 57) to A4 (69) — but FluidR3
# preset 109 stretches chromatically across 55-96 (empirical RMS sweep, no
# gaps), so the SF2 never clips a composition. RANGE_MIN/MAX = the practical
# GM-playable span; SOLO_RANGE/SWEET_SPOT = the chanter's real melodic zone
# (written range) where the patch is most idiomatic.
RANGE_MIN = 53      # F3 — conservative bottom of the GM patch's low register
RANGE_MAX = 96      # C7 — conservative top; chanter tops out at A4 (69)
SOLO_RANGE = (57, 69)   # A3-A4 — the REAL GHB chanter range (9 notes,
                        #   mixolydian on D: A B C# D E F# G A)
SWEET_SPOT = (62, 74)   # D4-D5 — chanter core (D4=62 is the modal center);
                        #   extends a 5th above for writing-room

# Register zones (relative to the GM patch, not the physical chanter)
ZONES = {
    "drone": (53, 56),   # F3-Bb3 — below chanter bottom: dark growl, only
                         #   usable as a pedal effect, NOT melody
    "chanter": (57, 69), # A3-A4 — the real 9-note chanter register (melody)
    "high": (70, 96),    # B4-C7 — GM patch extension above the physical
                         #   chanter: whistle/overblown, thin, less idiomatic
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (74, 1.0),    # steady blown tone — the bagpipe default (the
                             #   chanter never stops; tune = note changes)
    "skirl": (94, 0.35),     # gracenote-doubling attack (the GHB signature
                             #   "scream"); short, sharp, piercing
    "gracenote": (88, 0.15), # single-lead gracenote (G-D-E throws etc.) —
                             #   fast ornamental flick, always higher than
                             #   the main note
    "crisp": (80, 0.5),      # clean articulated note change (tongued)
    "accent": (92, 1.0),     # hard blow / top-hand emphasis on a long note
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",    # double reed, conical-ish bore: even+odd
                               #   harmonics (like oboe/sax, not odd-only clarinet)
    "mod_freq_ratio": 1.0,     # reed-driven oscillator, fundamental locked
    "mod_depth": 4.5,          # HIGH — the bagpipe's piercing, reedy scream
                               #   (oboe 2.5 / sax 2.8 / clarinet 2.0)
    "attack": 0.03,            # reeds already blown by bag pressure; a short
                               #   swell, not a 60 ms reed transient
    "release": 0.15,
}
MODAL_PRESET = "string"  # modal fallback: slow-decay harmonic stack for a
                         #   continuous tone (crude; no drone part)

# Production defaults
REVERB_TAIL = 2.4       # seconds, big hall/outdoor — the GHB lives outdoors;
                        #   long tail also masks chanter/drone beat roughness
EQ_BODY = (450, -3.0)   # peaking cut Hz, dB — tame chanter nasal honk/box
EQ_PRESENCE = (2500, 3.0)  # peaking boost Hz, dB — reed scream + grace-note cut
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — subtle breath/reed air
PAN = 0.0               # center for solo; drone-ish doubling L/R for band


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
