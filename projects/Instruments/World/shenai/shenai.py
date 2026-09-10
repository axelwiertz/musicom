# -*- coding: utf-8 -*-
"""Shenai — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity note: GM2 program 111 is the "Shanai" — the North Indian shehnai
(also "shenai"), a double-reed conical-bore oboe with a flared metal bell.
Spelling quirk: GM2 spec says "Shanai", FluidR3 preset 111 says "Shenai".
The shehnai is a continuous-tone monophonic melody instrument: a raga line
over a tanpura-style Sa-Pa drone, played with circular breathing. Composition
jobs should write modal melody lines over a pedal (drone) bass, NEVER dense
harmony.

Synthesis note: the primary recommendation is PhaseModSynth (a shehnai is a
self-sustained double-reed oscillator driven by airflow — phase-mod of a saw
carrier reproduces the bright even+odd harmonic reed spectrum, like oboe but
brighter: mod_depth 3.2 sits between oboe 2.5 and bagpipe 4.5). ModalSynth
preset 'string' (slow-decay harmonic stack) is a crude continuous-tone
fallback.
"""

MIDI_PROGRAM = 111
GM_NAME = "Shenai"
# RenderPipeline stem label: GM_PROGRAMS[111] = "Shanai" -> stem file
# trackXX_Shanai.wav. STEM_LABEL matches the pipeline's ACTUAL label
# (the GM-spec spelling "Shanai", not "Shenai") so stem-file lookups work.
# FluidR3 preset 111 = "Shenai" — cosmetic difference only.
STEM_LABEL = "Shanai"

# MIDI ranges (shehnai, sounding pitch)
# The physical shehnai sounds roughly D4 (62) to C6 (84) — about two octaves
# of melodic range. FluidR3 preset 111 stretches chromatically across 55-96
# (empirical RMS sweep, no gaps), so the SF2 never clips a composition.
# RANGE_MIN/MAX = the practical GM-playable span; SOLO_RANGE/SWEET_SPOT =
# the real melodic register where the patch is most idiomatic.
RANGE_MIN = 55      # G3 — conservative bottom of the GM patch's low register
RANGE_MAX = 96      # C7 — conservative top; physical shehnai tops out at C6 (84)
SOLO_RANGE = (62, 84)   # D4-C6 — the REAL shehnai register (~2 octaves)
SWEET_SPOT = (64, 79)   # E4-G5 — shehnai core solo register, fullest reed presence

# Register zones (relative to the GM patch, not the physical instrument)
ZONES = {
    "low": (55, 61),     # G3-B3 — below real register: dark, breathy low reed
    "solo": (62, 84),    # D4-C6 — the real shehnai melodic register (melody)
    "high": (85, 96),    # C#6-C7 — GM patch extension above the physical
                         #   shehnai: thin, whistle-y, less idiomatic
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (76, 1.0),    # steady blown tone — the shehnai default (circular
                             #   breathing; the line never stops, tune = note changes)
    "kan": (90, 0.12),       # grace-note flick ABOVE the main note — the
                             #   signature shehnai ornament (fast, ornamental)
    "meend": (72, 1.6),      # pitch slide across the register — vocal, plaintive
    "gamak": (86, 0.3),      # fast oscillating ornament around the main note
    "cut": (80, 0.5),        # tongued re-articulation (reed re-strike)
    "accent": (92, 1.0),     # hard reed overblow — sharp squeak, ceremonial
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth
FM_DEFAULTS = {
    "carrier_shape": "saw",    # double reed, conical-ish bore: even+odd
                               #   harmonics (like oboe/bagpipe)
    "mod_freq_ratio": 1.5,     # slight inharmonic offset — reed rasp
    "mod_depth": 3.2,          # bright reed — between oboe (2.5) and the
                               #   bagpipe scream (4.5)
    "attack": 0.06,            # real reed transient (the shehnai's sharp
                               #   squeaky onset), unlike bagpipe 0.03
    "release": 0.15,
}
MODAL_PRESET = "string"  # modal fallback: slow-decay harmonic stack for a
                         #   continuous tone (crude; no drone part)

# Production defaults
REVERB_TAIL = 2.0       # seconds, temple/darbar hall — ceremonial solo space
EQ_BODY = (450, -3.0)   # peaking cut Hz, dB — tame reed nasal honk/box
EQ_PRESENCE = (2600, 3.0)  # peaking boost Hz, dB — reed cut + ornament clarity
EQ_AIR = (7000, 1.5)    # highshelf Hz, dB — subtle reed/breath air
PAN = 0.0               # center for solo; slight L/R spread with sitar


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
