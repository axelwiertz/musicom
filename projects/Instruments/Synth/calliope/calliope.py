# -*- coding: utf-8 -*-
"""Calliope (Lead 3, GM82) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM82 "Lead 3 (calliope)" is the GM Lead-family patch modelled on
the steam calliope ("steam piano"): a bank of steam-driven organ pipes /
brass whistles played from a keyboard — the sound of circus, carnival,
fairground and Mississippi riverboat. The GM patch reads as a mellow,
slightly breathy pipe lead: near-sine pipe fundamentals with a touch of
chiff, fast valve-like attack, sustained while held. Synth-family fourth
entry alongside synth_pad (GM88), synth_brass_1 (GM62), synth_voice (GM54).

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
instruments and has NO calliope constant — use the raw GM number 82; the
registry is the full KB.

Synthesis note: primary is PhaseModSynth (sine carrier + gentle sine
modulation = the pipe fundamental with a whisper of chiff — the mellow
pipe-tone recipe; contrast the saw-carrier voices: synth brass, synth
voice). Additive pipe stack and the AirPipe physical model (pressure-driven
flue pipe, exactly the calliope's steam-pressure physics) are the fallbacks.
"""

MIDI_PROGRAM = 82
GM_NAME = "Lead 3 (calliope)"
# RenderPipeline stem label: GM_PROGRAMS[82] = "Lead 3 (calliope)" ->
# sanitized (spaces -> _, parens stripped) = Lead_3_calliope. FluidR3
# preset 82 = "Calliope Lead" (internal SF2 name differs cosmetically, no
# routing impact — stems are labelled from GM_PROGRAMS, not the SF2).
STEM_LABEL = "Lead_3_calliope"

# MIDI ranges (sounding pitch; the GM calliope patch plays the full
# keyboard — empirical FluidR3 sweep 24–108 all audible, no gaps — the band
# below is the idiomatic WRITING register: the real steam calliope rack is
# ~3 octaves around C4–C7)
RANGE_MIN = 60       # C4 — bottom of the pipe rack (below C4 the patch is
                     #   loud but reads as organ bass, not calliope)
RANGE_MAX = 96       # C7 — top of the pipe rack (above C7 it thins to a
                     #   whistle shimmer)
SOLO_RANGE = (67, 89)   # G4–A6 — solo-calliope focus (carnival melody band)
SWEET_SPOT = (72, 84)   # C5–C6 — the classic fairground tune register

# Register zones
ZONES = {
    "low": (60, 71),     # C4–B4 — pipe bottom: warm round, chunky
    "mid": (72, 83),     # C5–B5 — PRIMARY melody register (carnival tunes)
    "high": (84, 96),    # C6–C7 — bright top: whistle-y, cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pipe": (74, 1.0),      # held steam pipe — THE default gesture
    "chiff": (70, 0.30),    # short pipe burst — rhythmic carnival blips
    "marcato": (85, 0.85),  # hard valve onset — accented entrance
    "trill": (80, 0.25),    # fast repeated pipes — THE fairground ornament
    "swell": (64, 1.2),     # pressure swell — steam builds, note blooms
    "accent": (88, 0.9),    # downbeat hit — the calliope "yell"
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"  # sound/synthesis/phase_mod.py PhaseModSynth — a
                         #   sine carrier + gentle sine PM = the pipe
                         #   fundamental with a chiff whisper (mellow; the
                         #   saw-carrier recipes are for the brass/voice
                         #   siblings)
FM_DEFAULTS = {
    "carrier_shape": "sine",    # the pipe fundamental (NOT saw — calliope
                               #   pipes are near-sinusoidal; saw would
                               #   read as synth brass)
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,      # fundamental modulation — fattens the pure
                               #   sine into a pipe-like stack
    "mod_depth": 1.8,           # between flute 1.5 and shakuhachi 2.0 — a
                               #   pipe is brighter than a flute, mellower
                               #   than the reed voices (2.2–4.5)
    "attack": 0.02,             # fast valve opening (steam pressure is
                               #   already up — the note starts with the
                               #   key, not a breath transient)
    "release": 0.12,            # valve closes fast — dry pipe cutoff
    "sustain_level": 0.9,       # held while the gate is open
}
SYNTHESIS_DEFAULTS = {
    "instrument": "calliope",
    **FM_DEFAULTS,
}

# Additive alternative — mellow harmonic pipe stack (organ-pipe precedent:
# strong fundamental, gentle rolloff, no reed brightness)
ADDITIVE_DEFAULTS = {
    "harmonic_count": 6,
    "harmonic_weights": [1.0, 0.55, 0.30, 0.18, 0.10, 0.05],
    "attack": 0.02,
    "release": 0.12,
}

# AirPipe physical model (tertiary) — sound/synthesis/air_pipe.py: a
# pressure-driven flue pipe IS the calliope physics (steam pressure = the
# air supply; pressure 0.6 sits below the 0.75 overblow threshold so the
# pipe stays on the fundamental)
AIRPIPE_DEFAULTS = {
    "stopped": False,       # open pipe (full harmonic series)
    "pressure": 0.6,        # full but not overblowing
    "length_scale": 1.0,
}

# Production defaults
REVERB_TAIL = 2.0       # seconds — fairground space: open-air big-top,
                        #   medium tail (calliope phrases are rhythmic, so
                        #   shorter than the pad family; the notes carry
                        #   their own steam)
EQ_BODY = (400, -2.5)   # peaking cut Hz, dB — pipe-stack low-mid boxiness
EQ_PRESENCE = (3000, 2.0)  # peaking boost Hz, dB — the whistle/presence
                           #   band (calliope brightness + chiff clarity)
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — steam-hiss shimmer
PAN = 0.0               # center for the composed stem; ±0.3 L/R spread on
                        #   wide pipe-rack choruses


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
