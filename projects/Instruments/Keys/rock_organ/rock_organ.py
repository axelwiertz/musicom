# -*- coding: utf-8 -*-
"""Rock Organ (overdriven tonewheel/transistor combo organ) — musicom constants.

GM18 = Rock Organ. This is NOT a second drawbar-organ entry: GM16 (Drawbar
Organ) is the clean jazz/gospel B-3 patch, while GM18 is the *amplified*
organ of rock — the same tonewheel or transistor-combo source pushed through a
hot tube amp and a Leslie, i.e. Jon Lord (Deep Purple, Hiwatt + Marshall
stacks), Keith Emerson (L-100 through fuzz), Booker T. Jones ("Green Onions",
M3), Steve Winwood, Rick Wright, Gregg Allman, and the ska/rocksteady school
(Jackie Mittoo). The defining difference from GM16 is **saturation**: the
flat-topped waveform adds odd harmonics and mid-band compression that turns
the organ into a cutting, sustaining lead/rhythm voice rather than a pad.

Synthesis is literally additive here: 91 tonewheels produce sine partials and
the nine drawbars mix them. The overdrive stage is a post-additive waveshaper,
not a separate oscillator bank.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, registrations, articulations and synthesis defaults.
"""

MIDI_PROGRAM = 18
GM_NAME = "Rock Organ"
# RenderPipeline stem label: GM_PROGRAMS[18] = "Rock Organ" ->
# trackXX_Rock_Organ.wav (labels match exactly, no quirk).
STEM_LABEL = "Rock_Organ"

# MIDI ranges (sounding pitch, non-transposing)
RANGE_MIN = 36       # C2 — bottom key of a 61-key manual / M-3 bass octave
RANGE_MAX = 96       # C7 — top of the manual (2' drawbar to C7)
SOLO_RANGE = (48, 84)   # C3–C6 — right-hand lead/comp register
SWEET_SPOT = (55, 79)   # G3–G5 — saturated mids cut without mud

# Register zones
ZONES = {
    "bass": (36, 55),    # C2–G3 — left-hand key bass, 16'+8' only, riff roots
    "mid": (56, 79),     # G#3–G5 — primary comp/lead register, full drawbars
    "high": (80, 96),    # G#5–C7 — screaming top, 1' partial, solos and stabs
}

# Articulation defaults (velocity, duration_factor).
# A tonewheel key contact is binary — velocity is a MIX/ATTACK value, not a
# dynamic. Real dynamics come from drawbars, swell pedal and note density.
ARTICULATIONS = {
    "sustain": (85, 1.0),      # held chord/note, no decay while key is down
    "stab": (94, 0.22),        # short percussive hit — the rock/ska rhythm cell
    "chop": (78, 0.10),        # very short muted chop, key-click dominated
    "percussion": (90, 0.35),  # key-on 2nd/3rd-harmonic ping, fast decay
    "key_click": (72, 0.06),   # busbar contact transient only (no tone)
    "accent": (100, 0.85),     # full drawbars + percussion on a downbeat
    "smear": (66, 0.90),       # chromatic palm smear / glissando fill
    "swell": (96, 1.0),        # pedal-swelled long note, crescendo target
}

# Synthesis engine recommendation
SYNTHESIS = "additive"     # sound/synthesis/additive.py (SoundWave)

# Nine drawbars, console order: label -> harmonic ratio vs 8' (1.0).
# 5 1/3' is a twelfth above the fundamental (3x) on the Hammond busbar layout
# used here, 16' is the sub-octave (0.5x). Non-integer-only registrations
# should go through drawbar_harmonics(); ADDITIVE_HARMONICS below is the
# engine-friendly integer-partial bank.
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

# Registrations as nine levels 0-8 (console order above).
DRAWBAR_PRESETS = {
    "rock": (8, 8, 8, 6, 4, 2, 0, 0, 0),    # Jon Lord / Emerson body
    "scream": (8, 8, 8, 8, 8, 8, 6, 4, 8),  # full-out solo, all bars
    "ska": (8, 6, 8, 4, 2, 0, 0, 0, 0),     # Jackie Mittoo bright stabs
    "booker": (8, 0, 8, 4, 0, 0, 0, 0, 0),  # "Green Onions" M3 comp
    "gospel": (8, 8, 8, 8, 6, 4, 0, 0, 0),  # wide scream when pushed
    "bass": (8, 0, 8, 0, 0, 0, 0, 0, 0),    # left-hand/pedal roots
    "ballad": (8, 0, 8, 0, 0, 0, 0, 0, 0),  # soft 16'+8' verse bed
}

# Engine-compatible integer-partial banks. Amplitudes are human-readable;
# the additive engine normalizes them (sum == 1.0). Rock Organ banks carry
# MORE even *and* odd upper partials than the clean Drawbar Organ banks —
# that extra 4x/6x/8x content is the saturated "bark".
ADDITIVE_HARMONICS = {
    # partials:  1x     2x     3x     4x     5x     6x     7x     8x
    "rock":   [1.00, 0.85, 0.75, 0.55, 0.40, 0.30, 0.15, 0.22],
    "scream": [1.00, 0.95, 0.90, 0.75, 0.60, 0.50, 0.30, 0.40],
    "ska":    [1.00, 0.80, 0.85, 0.45, 0.25, 0.12, 0.00, 0.08],
    "booker": [1.00, 0.60, 0.55, 0.30, 0.10, 0.05, 0.00, 0.00],
    "gospel": [1.00, 0.90, 0.85, 0.65, 0.50, 0.40, 0.18, 0.28],
    "bass":   [1.00, 0.55, 0.00, 0.18, 0.00, 0.00, 0.00, 0.00],
    "ballad": [1.00, 0.20, 0.00, 0.05, 0.00, 0.00, 0.00, 0.00],
}

# ADSR for the additive path: contact closure, flat sustain, fast key-off.
ADDITIVE_ENVELOPE = {
    "attack": 0.003,     # s — busbar contact (slightly harder than GM16)
    "decay": 0.0,        # s — tonewheel output is flat while held
    "sustain": 1.0,
    "release": 0.045,    # s — key-off cut + click
}

# Overdrive stage (post-additive waveshaper — the "rock" in Rock Organ)
OVERDRIVE_DEFAULTS = {
    "drive": 2.6,            # tanh gain into the clipper (GM16 clean ≈ 1.0)
    "tone_hz": 2400,         # post-clip low-pass corner (cabinet rolloff)
    "output_trim_db": -3.0,  # compensate the level the clipper adds
    "asymmetry": 0.15,       # tube-style even-harmonic bias, 0 = symmetric
}

# Leslie rotating-speaker model — rock players park it on FAST
MOTOR_DEFAULTS = {
    "rate_hz": 6.9,               # tremolo (fast) horn speed
    "depth": 0.34,                # a little deeper than the clean GM16 patch
    "rate_range_hz": (0.8, 7.0),  # chorale <-> tremolo
    "doppler_cents": 7.0,         # pitch wobble from the rotating horn
    "accel_s": 0.8,               # spin-up time chorale -> tremolo
}

# PhaseModSynth alternative (cheap FM rock organ, DX7-ish)
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.0,   # adds the 3rd harmonic the percussion tab gives
    "mod_depth": 3.2,
    "attack": 0.003,
    "release": 0.05,
}

# Production defaults
REVERB_TAIL = 1.3        # seconds — club/stage, NOT cathedral; amp is close-
                         # mic'd and the Leslie is directional
EQ_BODY = (250, -1.5)    # peaking cut Hz, dB — clear 16' mud under the drive
EQ_PRESENCE = (1800, 3.0)  # peaking boost Hz, dB — the saturated mid bark
EQ_AIR = (7000, 1.5)     # highshelf Hz, dB — key click + rotor top
PAN = 0.0                # centre; ±0.2–0.35 when doubled with a clean organ


def drawbar_harmonics(registration=DRAWBAR_PRESETS["rock"]):
    """Map a nine-level drawbar registration to {harmonic_ratio: gain}.

    Levels are 0-8 on the console; gain is level/8 (linear busbar mixing).
    Ratios include the 0.5x sub-octave (16') and 1.5x quint (5 1/3') that
    integer-partial engines cannot express — use for custom additive renders.
    """
    out = {}
    for (label, ratio), level in zip(DRAWBAR_FOOTAGES, registration):
        if level:
            out[ratio] = round(level / 8.0, 4)
    return out


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
