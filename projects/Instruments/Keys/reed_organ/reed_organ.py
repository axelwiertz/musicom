# -*- coding: utf-8 -*-
"""Reed Organ (Harmonium) — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the primary recommendation is PhaseModSynth (free-reed
aerophone — sound/synthesis/phase_mod.py). A saw carrier with moderate
modulation reproduces the reed organ's distinctive warm/nasal tone. The
free-reed physics is the same as the accordion and harmonica, but the
reed organ's cabinet resonance (wind chest + wooden resonator box) adds
body and a characteristic "cabinet honk" absent from the smaller handheld
free-reed instruments.

Identity: GM20 = Reed Organ / Harmonium / Pump Organ — covers the American
reed organ (suction, foot-pumped), the European harmonium (pressure,
foot-pumped), and the Indian hand-pumped harmonium. A fully polyphonic
instrument — melody, harmony, drone chord all at once. NOT a monophonic
lead voice. Used in 19th-century American parlors, European churches,
Indian classical/traditional (where it is the ubiquitous melodic drone
instrument), and gospel/sacred music worldwide.
"""

MIDI_PROGRAM = 20
GM_NAME = "Reed Organ"
# RenderPipeline stem label: GM_PROGRAMS[20] = "Reed Organ" -> stem file
# trackXX_Reed_Organ.wav (matches exactly, no quirk; FluidR3 preset 20 =
# "Reed Organ")
STEM_LABEL = "Reed Organ"

# MIDI ranges (full-size 5-octave harmonium, sounding pitch)
RANGE_MIN = 36      # C2 — lowest 8' bass reed on full-size cabinet
RANGE_MAX = 96      # C7 — extended treble top
SOLO_RANGE = (48, 84)   # C3–C6 — full expressive range of standard 49-key instrument
SWEET_SPOT = (60, 84)   # C4–C6 — primary melodic register, richest reed/cabinet tone

# Register zones
ZONES = {
    "bass": (36, 47),      # C2–B2 — 8' bass reeds: dark, rumbling, drone foundation
    "low": (48, 59),       # C3–B3 — tenor register: warm, reedy, cello-like
    "mid": (60, 76),       # C4–E5 — primary melodic register: richest, sweetest cabinet tone
    "high": (77, 89),      # F5–F6 — 4' treble register: bright, cutting, accordion-like
    "extended": (90, 96),  # G6–C7 — thin/piercing, lowest reed density at top
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "sustain": (74, 1.0),    # steady bellows, held note — default
    "staccato": (78, 0.2),   # short bellows pulse, crisp release
    "legato": (68, 1.0),     # smooth connected notes, minimal bellows change
    "marcato": (86, 0.85),   # hard bellows accent, strong cabinet resonance
    "sforzando": (92, 0.8),  # sudden forceful bellows push
    "tremolo": (70, 0.6),    # bellows shake — amplitude vibrato via foot-pump wobble
}

# Synthesis engine recommendation
SYNTHESIS = "phase_mod"   # sound/synthesis/phase_mod.py PhaseModSynth (free-reed)
FM_DEFAULTS = {
    "carrier_shape": "saw",     # free reed = symmetric oscillator: even+odd
                                #   harmonics (like accordion/sax family)
    "mod_freq_ratio": 1.0,      # reed-driven oscillator, fundamental locked
    "mod_depth": 3.5,           # moderate-high — harmonium cabinet resonance is
                                #   more nasal/buzzy than accordion (3.2) but
                                #   less piercing than bagpipe (4.5); the
                                #   wooden resonator box adds body to the buzz
    "attack": 0.04,             # moderate — bellows must fill the wind chest;
                                #   slower than accordion (0.015) but faster
                                #   than pipe organ (0.06)
    "release": 0.06,            # reed stop on bellows release; the wind chest
                                #   gives a brief sustain after bellows stop
}
MODAL_PRESET = "string"  # modal fallback: sustained harmonic stack, clean

# Production defaults
REVERB_TAIL = 1.6       # seconds, room/chamber — harmonium is dry but cabinet
                        #   resonance gives a natural bloom; keep reed clarity
EQ_BODY = (250, -2.5)   # peaking cut Hz, dB — tame wind chest cabinet honk
EQ_PRESENCE = (2200, 2.5)  # peaking boost Hz, dB — reed definition and cut
EQ_AIR = (7500, 1.5)    # highshelf Hz, dB — subtle reed buzz sparkle
PAN = 0.0               # center for solo; ±0.15-0.25 for stereo layering


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)