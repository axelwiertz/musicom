# -*- coding: utf-8 -*-
"""Steel-String Acoustic Guitar — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Synthesis note: the steel-string acoustic guitar (GM26) is a plucked steel
waveguide. Karplus-Strong is the primary recommendation (stiff steel string
with pick excitation, loop_gain 0.9970 for 1–3 s ring, noise_component 0.02
for pick scrape). ModalSynth 'string' preset is the fallback.

Identity: GM26 = steel-string acoustic guitar (the dominant folk/country/rock
rhythm and fingerpicking voice), NOT the nylon-string acoustic (GM25) and NOT
an electric guitar. Standard tuning E2-A2-D3-G3-B3-E4 (MIDI 40, 45, 50, 55,
59, 64). Six-string, 20-fret fingerboard, ~6 octave range including harmonics.
"""

MIDI_PROGRAM = 25
GM_NAME = "Acoustic Guitar (steel)"
# RenderPipeline stem label: GM_PROGRAMS[25] = "Acoustic Guitar (steel)"
#   -> stem file trackXX_Acoustic_Guitar_steel.wav (matches pipeline label;
#   FluidR3 preset 25 = "Steel String Guitar" — internal SF2 name "Steel String
#   Guitar" vs pipeline "Acoustic Guitar (steel)" is cosmetic only, no routing
#   impact)
STEM_LABEL = "Acoustic Guitar (steel)"

# MIDI ranges (standard steel-string acoustic, sounding pitch)
RANGE_MIN = 40      # E2 — open 6th string
RANGE_MAX = 86      # C#6 — 20th fret high E string
SOLO_RANGE = (50, 79)   # D3–G5 — richest fingerpicking/flatpick lead zone
SWEET_SPOT = (50, 79)   # D3–G5 — strongest fundamental, best projection

# Register zones
ZONES = {
    "low": (40, 50),     # E2–D3 — bass strings (E A D), open chord roots, bass runs
    "mid": (51, 66),     # D#3–G4 — full fundamental for chords and fingerpicking
    "high": (67, 86),    # G#4–C#6 — melodic lead, harmonics, bright cutting top
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "strum_down": (80, 0.25),     # full down-strum, percussive, ringing sustain
    "strum_up": (70, 0.20),       # lighter upward sweep, less percussive
    "fingerpick_thumb": (65, 1.0),  # warm round thumb attack (bass strings)
    "fingerpick_index": (60, 1.0),  # medium attack, balanced treble tone
    "flatpick": (85, 0.20),       # bright aggressive pick strike — cutting drive
    "arpeggio": (65, 0.15),       # rolled fingerpicked chord, fluid texture
    "hammer_on": (75, 0.5),       # legato slur upward from hammering finger
    "pull_off": (65, 0.5),        # legato slur downward from pulling finger
    "muted_palm": (45, 0.10),     # palm rest on bridge — damped percussive "chunk"
    "harmonic": (95, 0.45),       # bell-like natural overtone (12th/7th/5th fret)
    "slide": (70, 0.8),           # continuous pitch glide between two frets
    "accent": (92, 0.20),         # hard aggressive downstroke — cutting downbeat
}

# Synthesis engine recommendation
SYNTHESIS = "karplus_strong"  # sound/synthesis/karplus_strong.py KSModel
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,        # steel strings ring 1–3 s (between clavi 0.9960 and harp 0.9985)
    "excitation": "pick",       # bright hard attack from plectrum
    "width": 0.65,              # moderate pulse width (stiffer than nylon = brighter)
    "lowpass_hz": 6000,         # steel has energy up to ~8 kHz, lowpass 6k for mix-friendly tone
    "noise_component": 0.02,    # pick scrape noise on wound strings
}
MODAL_DEFAULTS = {
    "preset": "string",         # ModalSynth 'string' preset — harmonic 1D string modes
    "excitation": "impulse",    # struck excitation (pick/finger transient)
    "decay_rates": [6, 9, 14, 20, 30],  # moderate decays for the string modes
}

# Production defaults
REVERB_TAIL = 1.6       # seconds, room/small hall — steel rhythm needs clarity
EQ_BODY = (300, -3.0)   # peaking cut Hz, dB — reduce boxiness/honk at 200–400 Hz
EQ_PRESENCE = (4000, 2.5)  # peaking boost Hz, dB — string brightness and pick attack
EQ_AIR = (9000, 1.5)    # highshelf Hz, dB — gentle air/sparkle on upper harmonics
PAN = -0.2              # center for solo; ±0.2 for stereo double-tracked rhythm


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)