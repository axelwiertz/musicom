# -*- coding: utf-8 -*-
"""Honky-tonk Piano — musicom instrument constants.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, articulations, and synthesis defaults in one place.

Identity: GM 3 = Honky-tonk Piano (0-based program 3 = the 4th GM entry).
The sound is a piano whose unison strings are deliberately out of tune with
each other and whose hammers are often hardened — the "tack piano" / saloon
piano / barrelhouse upright of ragtime, stride, boogie-woogie and country
honky-tonk. It is NOT a "bad" piano: the detuned unisons are a deliberate
chorusing/beating effect that lets the instrument cut through a noisy bar
with no PA.

Synthesis note: primary is ModalSynth (sound/synthesis/modal.py) with a custom
HONKY_TONK_MODES bank: every string partial is doubled at a detuned twin
(~+17 cents, amplitude 0.8) so the bank itself BEATS at 2-6 Hz — the honky
identity. Additive is the secondary (detuned harmonic stack, stack=2, detune
±0.010 = the same beating by a different route); PhaseModSynth is the tertiary
FM-piano fallback.

Enum note: `structures/instrument.py` `MidiInstrument` exposes only 10
instruments and has NO honky-tonk constant — use the raw GM number 3; the
registry is the full KB.
"""

MIDI_PROGRAM = 3
GM_NAME = "Honky-tonk Piano"
# RenderPipeline stem label: GM_PROGRAMS[3] = "Honky-tonk Piano" -> sanitized
# stem file trackXX_Honky-tonk_Piano.wav (spaces -> _, hyphen KEPT — the
# sanitizer only strips parens and slashes).
STEM_LABEL = "Honky-tonk_Piano"

# MIDI ranges (sounding pitch). A piano is A0–C8, but the honky-tonk patch is
# thin and clangy below A1 and airless above C7 — that band is the idiomatic
# writing compass (see empirical FluidR3 sweep in instrument.md).
RANGE_MIN = 33      # A1 — stride/boogie left-hand bottom (below this: mud)
RANGE_MAX = 96      # C7 — top of the ragtime right hand / gliss run
SOLO_RANGE = (48, 84)   # C3–C6 — solo/comping focus (mid body + honk)
SWEET_SPOT = (55, 84)   # G3–C6 — the honky "nasal" band, fullest bark

# Register zones
ZONES = {
    "bass": (33, 47),      # A1–B2 — stride/boogie LH: octaves, tenths, walking
    "mid_low": (48, 59),   # C3–B3 — chord comping body, the "saloon" honk
    "mid": (60, 71),       # C4–B4 — ragtime melody + right-hand chords
    "high": (72, 96),      # C5–C7 — ragtime runs, octave tremolo, gliss
}

# Articulation defaults (velocity, duration_factor)
ARTICULATIONS = {
    "ragtime_melody": (88, 0.95),   # crisp syncopated RH line — the default
    "stride_bass": (92, 0.50),      # LH "oom" — short, percussive low octave
    "stride_chord": (80, 0.40),     # LH/backbeat "pah" — clipped off-beat chord
    "boogie_ostinato": (85, 0.45),  # rolling eighth-note LH figure
    "comp_chop": (76, 0.30),        # country/pop honky comp stab
    "octave_tremolo": (82, 1.0),    # alternating octaves, fast repeated notes
    "glissando": (95, 0.90),        # white-key rake — runs read as one gesture
    "tack_accent": (108, 0.85),     # hard tack-hammer hit — metallic clack
    "sustain_wash": (58, 1.0),      # pedal down, chord rings into the room
    "dead_thud": (44, 0.18),        # damped/dud note — comic saloon "plunk"
}

# Synthesis engine recommendation
SYNTHESIS = "modal"     # ModalSynth — struck-string inharmonic bank
MODAL_PRESET = "string"  # closest stock bank (harmonic stack, moderate decay)

# Custom modal bank (A4 reference): each partial is DOUBLED at a detuned twin
# (+17 cents, amp 0.8) — the beating IS the instrument. Ratios carry a small
# stretch (piano inharmonicity, B ≈ 1e-4).
HONKY_TONK_MODES = [
    (440.0, 1.00, 0.70),    # f0 — string A of the unison
    (444.3, 0.80, 0.72),    # f0 +17c — string B: 4.3 Hz beat against A
    (881.5, 0.55, 0.95),    # 2nd partial (2.004x, stretched)
    (890.1, 0.44, 0.98),    # 2nd partial twin
    (1325.0, 0.32, 1.20),   # 3rd partial (3.011x)
    (1337.9, 0.26, 1.24),   # 3rd partial twin
    (1773.9, 0.18, 1.50),   # 4th partial (4.031x)
    (1791.2, 0.14, 1.55),   # 4th partial twin
    (2227.7, 0.10, 1.90),   # 5th partial (5.063x)
    (2687.0, 0.06, 2.40),   # 6th partial (6.107x) — hammer/tack clack zone
]

# Additive alternative: detuned harmonic stack. Weights are RELATIVE
# (normalize to sum 1.0 before apply_overtones — the API asserts sum == 1.0).
ADDITIVE_HARMONICS = {
    # Strong fundamental + a lifted 2nd/3rd: the honky "nasal" midrange.
    "honky_tonk": [1.0, 0.62, 0.44, 0.27, 0.16, 0.09, 0.04],
}
SYNTHESIS_DEFAULTS = {
    "instrument": "honky_tonk",
    "attack": 0.004,     # hard hammer on a hard string — near-instant
    "detune": 0.010,     # ±1.0% ≈ ±17 cents — the unison beating (identity)
    "stack": 2,          # exactly TWO detuned strings = the classic honky pair
    "release": 0.25,     # dampers bite quickly (upright action, not grand)
    "sustain_level": 0.55,
    "decay_S": 1e-4,     # additive long-hold quirk (same as pad entries)
}

# PhaseModSynth tertiary — FM piano (DX-style), mild depth
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 2.01,   # slightly stretched 2nd partial
    "mod_depth": 1.6,         # moderate FM index (Rhodes 1.8, harpsichord 2.2);
                              #   the tack clack comes from the attack, not depth
    "attack": 0.003,
    "release": 0.35,
    "sustain_level": 0.5,
}

# Production defaults
REVERB_TAIL = 1.4       # seconds — a small wooden ROOM, not a hall: the
                        #   honky-tonk is a close-miked bar upright
EQ_BODY = (300, -2.0)   # peaking cut Hz, dB — upright cabinet boom
EQ_PRESENCE = (1800, 2.5)  # peaking boost Hz, dB — the nasal honk band
EQ_AIR = (8000, 1.5)    # highshelf Hz, dB — tack/hammer clack air
PAN = 0.0               # centre; slight -0.15 if doubled with a clean piano


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
