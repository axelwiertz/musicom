# -*- coding: utf-8 -*-
"""Drawbar Organ (Hammond tonewheel) — musicom instrument constants.

GM16 = Drawbar Organ. The electromechanical tonewheel organ (Hammond B-3 /
C-3): 91 toothed wheels generate sine partials that the player mixes with
nine drawbars per manual. It is the ONLY common orchestral/pop instrument
whose timbre is *literally* additive synthesis, so the additive engine is a
physical model here, not an approximation.

Reference range: 25-note pedal board C1-C3 (MIDI 24-48) plus two 61-key
manuals F1-F6 (MIDI 29-89). The GM patch (FluidR3 preset 16) spans that span.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, drawbar registrations, articulations and synthesis defaults.
"""

MIDI_PROGRAM = 16
GM_NAME = "Drawbar Organ"
# RenderPipeline stem label: GM_PROGRAMS[16] = "Drawbar Organ" ->
# trackXX_Drawbar_Organ.wav (labels match exactly, no quirk)
STEM_LABEL = "Drawbar_Organ"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 24       # C1 — bottom of the 25-note pedal board
RANGE_MAX = 89       # F6 — top key of the 61-key manual
SOLO_RANGE = (48, 84)   # C3-C6 — right-hand solo/comp register
SWEET_SPOT = (55, 79)   # G3-G5 — 8'/4'/2 2/3' drawbars cut without mud

# Register zones
ZONES = {
    "pedal": (24, 48),        # C1-C3 — pedal board, 16'+8' only, bass roots
    "lower": (29, 65),        # F1-F4 — left-hand comping, chords, key bass
    "upper": (48, 89),        # C3-F6 — right-hand lead, stabs, swoops
}

# Articulation defaults (velocity, duration_factor)
# A tonewheel organ is NOT velocity sensitive: the key contact is a binary
# switch. Velocity here is a mix-balance value; get dynamics from drawbars,
# the swell pedal and note density.
ARTICULATIONS = {
    "sustain": (85, 1.0),       # held key, all drawbars flat, no decay
    "legato": (80, 1.0),        # overlapping smear, no re-attack click
    "staccato": (70, 0.18),     # short stab — key click dominates
    "percussion": (88, 0.35),   # 2nd/3rd-harmonic ping on key-on, fast decay
    "key_click": (74, 0.06),    # broadband busbar-contact transient only
    "accent": (96, 0.85),       # full drawbars + percussion, downbeat stab
    "palm_smear": (64, 0.9),    # chromatic palm smear / glissando
    "bass_pedal": (82, 0.95),   # pedal-board root, long held
}

# Synthesis engine recommendation
SYNTHESIS = "additive"     # sound/synthesis/additive.py (SoundWave)

# The nine drawbars, in console order: label -> harmonic ratio vs 8' (1.0).
# 5 1/3' is a FIFTH above the fundamental (1.5x) and 16' is a sub-octave
# (0.5x) — neither is an integer partial, which is why drawbar_harmonics()
# exists alongside the engine-friendly ADDITIVE_HARMONICS bank.
DRAWBAR_FOOTAGES = (
    ("16'", 0.5),
    ("5 1/3'", 1.5),
    ("8'", 1.0),
    ("4'", 2.0),
    ("2 2/3'", 3.0),
    ("2'", 4.0),
    ("1 3/5'", 5.0),
    ("1 1/3'", 6.0),
    ("1'", 8.0),
)

# Classic registrations as nine levels 0-8 (console order above).
DRAWBAR_PRESETS = {
    "full": (8, 8, 8, 8, 8, 8, 8, 8, 8),        # everything out
    "jazz": (8, 8, 8, 0, 0, 0, 0, 0, 0),        # 888000000 — the hollow one
    "gospel": (8, 8, 8, 8, 6, 4, 0, 0, 0),      # wide, scream when pushed
    "flute": (8, 0, 8, 0, 0, 0, 0, 0, 0),       # 808000000 — soft 8'/16'
    "perc": (8, 8, 8, 0, 0, 0, 0, 0, 0),        # jazz + percussion tab on
    "bass": (8, 0, 8, 0, 0, 0, 0, 0, 0),        # pedal: 16' + 8'
    "ska": (8, 6, 8, 4, 0, 0, 0, 0, 0),         # bright rhythmic stabs
}

# Engine-compatible integer-partial banks (apply_overtones sums partials at
# 1x, 2x, 3x ... of the MIDI fundamental). Human-readable amplitudes; the
# engine requires normalization (sum == 1.0) — see verify_drawbar_organ.py.
ADDITIVE_HARMONICS = {
    # partials:  1x    2x    3x    4x    5x    6x    7x    8x
    "full":   [1.00, 0.90, 0.75, 0.60, 0.45, 0.30, 0.12, 0.15],
    "jazz":   [1.00, 0.85, 0.95, 0.00, 0.00, 0.00, 0.00, 0.00],
    "gospel": [1.00, 0.90, 0.80, 0.70, 0.50, 0.40, 0.10, 0.20],
    "flute":  [1.00, 0.15, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    "pedal":  [1.00, 0.60, 0.00, 0.20, 0.00, 0.00, 0.00, 0.00],
}

# ADSR for the additive path: attack = contact closure, NO decay, sustain
# 1.0 (tonewheel output is flat while held), short key-off release.
ADDITIVE_ENVELOPE = {
    "attack": 0.004,        # s — busbar contact closure
    "decay": 0.0,           # s — no decay stage
    "sustain": 1.0,         # full level held
    "release": 0.05,        # s — key-off cut + click
}

# PhaseModSynth alternative (DX7-style FM organ)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,    # 2nd partial pair — the FM organ staple
    "mod_depth": 2.5,
    "attack": 0.004,
    "release": 0.05,
}

# Leslie rotating-speaker model (optional production stage)
MOTOR_DEFAULTS = {
    "rate_hz": 6.9,               # tremolo (fast) horn speed
    "depth": 0.30,                # amplitude-modulation depth (0-1)
    "rate_range_hz": (0.7, 7.0),  # chorale 0.7 Hz -> tremolo 7.0 Hz
    "doppler_cents": 6.0,         # pitch wobble from the rotating horn
    "accel_s": 1.0,               # spin-up time chorale -> tremolo
}

# Production defaults
REVERB_TAIL = 1.8        # seconds, live room — Leslie cabinet in a club,
                         #   not a cathedral (Church Organ gets 2.2 s)
EQ_BODY = (200, -2.0)    # peaking cut Hz, dB — clear 16'-drawbar mud
EQ_PRESENCE = (2500, 2.0)  # peaking boost Hz, dB — key click + percussion
EQ_AIR = (8000, 1.0)     # highshelf Hz, dB — air on the click transient
PAN = 0.0                # centre; +0.2 with rotor modulation is a taste call


def drawbar_harmonics(registration=DRAWBAR_PRESETS["jazz"]):
    """Map a nine-level drawbar registration to {harmonic_ratio: gain}.

    Levels are 0-8 on the console; gain is level/8 (linear, matching the
    organ's resistive busbar mixing). Ratios include the 0.5x sub-octave
    (16') and 1.5x quint (5 1/3') that integer-partial engines cannot
    express, so use this for custom additive renders.
    """
    out = {}
    for (label, ratio), level in zip(DRAWBAR_FOOTAGES, registration):
        if level:
            out[ratio] = round(level / 8.0, 4)
    return out


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
