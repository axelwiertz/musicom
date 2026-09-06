# -*- coding: utf-8 -*-
"""Banjo — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is Karplus-Strong (plucked
waveguide — SP-011, sound/synthesis/karplus_strong.py). A banjo is a
short-scale stringed instrument with a taut Mylar/animal-skin head — the
vibrating membrane is the whole tone. The waveguide maps that to a loop_gain
BELOW the koto (0.9970) and sitar (0.9975): ~0.9960 gives the banjo's
snappy, bright, fast-decaying ring — clawhammer bite, not darbar sustain.
The ModalSynth MODAL_PRESET 'string' bank is the alternative "clean banjo"
patch (harmonic stack, loses the head snap).

Scruggs/three-finger (bluegrass) and clawhammer (old-time) are the two
classic right-hand styles; the banjo is a LINE + RHYTHM instrument — roll
patterns (T-I-M-T-M-I-T-M), not dense chromatic harmony. Composition jobs
should write melodic/roll lines and rhythmic backup strums, not thick chords.
"""

MIDI_PROGRAM = 105
GM_NAME = "Banjo"
# RenderPipeline stem label: GM_PROGRAMS[105] = "Banjo" -> stem file
# trackXX_Banjo.wav (matches exactly, no quirk; FluidR3 preset 105 = "Banjo")
STEM_LABEL = "Banjo"

# MIDI ranges (5-string banjo, sounding pitch; open G tuning gDGBD)
RANGE_MIN = 46      # A#2 — bottom of the 4th (C) string on a standard 5-string
RANGE_MAX = 93      # A6 — practical top of the 1st (D) string, capo territory
SOLO_RANGE = (60, 84)   # C4–C6 — solo repertoire focus (melodic/Scruggs rolls)
SWEET_SPOT = (62, 81)   # D4–A5 — best head snap + string cut

# Register zones
ZONES = {
    "low": (46, 59),     # A#2–B3 — 4th/5th strings (C & g) — dark, thumpy head
    "mid": (60, 74),     # C4–D5 — 3rd/2nd strings (G & B) — primary melodic register
    "high": (75, 93),    # D#5–A6 — 1st string (D) — bright, thin, cutting
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "pluck": (82, 1.0),     # standard finger/roll stroke — full head snap + decay
    "roll": (74, 0.12),     # Scruggs T-I-M-T-M-I-T-M roll — fast, rhythmic
    "hammer": (88, 0.35),   # hammer-on — bright, ornamental, no pick transient
    "pull": (70, 0.3),      # pull-off — softer, descending snap
    "choke": (48, 0.12),    # damped/choked stroke — dry, percussive (clawhammer)
}

# Synthesis engine recommendation
SYNTHESIS = "karplus"   # Karplus-Strong plucked waveguide (SP-011)
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9960,    # moderate damping -> snappy bright ring (~1-1.5 s);
                            #   below koto 0.9970 / sitar 0.9975 — head snap, dry
    "width": 0.40,          # tight focus (narrower than koto's 0.45)
    "role": "lead",
}
MODAL_PRESET = "string"  # modal resonator fallback (generic plucked string)

# Phase-mod alternative patch (cheap banjo)
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 2.2,
    "mod_depth": 3.2,
    "attack": 0.002,
    "release": 0.18,
}

# Production defaults
REVERB_TAIL = 1.0       # seconds, room — dry rhythmic banjo; keep the head
                        #   snap clear (shamisen 1.2 / koto 1.4 / sitar 2.2)
EQ_BODY = (280, -2.5)   # peaking cut Hz, dB — tame head/membrane boxiness
EQ_PRESENCE = (3000, 2.5)  # peaking boost Hz, dB — head snap + string cut
EQ_AIR = (8000, 1.0)    # highshelf Hz, dB — subtle air, keep twang not harsh
PAN = 0.0               # center for solo; +0.2..0.3 spread for ensembles


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
