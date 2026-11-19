# -*- coding: utf-8 -*-
"""Percussive Organ (tonewheel organ with the key-on percussion tab) — constants.

GM17 = Percussive Organ. This is the third Hammond-family GM patch and NOT a
duplicate of its neighbours:

* GM16 Drawbar Organ — clean B-3, drawbars only, no percussion tab.
* GM17 Percussive Organ (this file) — same tonewheel source with the
  **percussion tab** engaged: a fast-decaying 2nd or 3rd harmonic "ping" on
  every key-on, plus a brighter, thinner drawbar registration. This is the
  jazz/funk/gospel/soul comp voice — Jimmy Smith, Jimmy McGriff, Booker T.
  on the bright stops, Billy Preston, the "Green Onions"-era rhythm sound.
* GM18 Rock Organ — the same source pushed through a saturated amp.
* GM19 Church Organ — pipes, not tonewheels (no percussion, no drawbars).

The percussion tab is what makes this patch *articulate*: each note gets a
transient that cuts through a dense mix without extra velocity, which is why
it is the classic funk/soul comping organ.

Companion to instrument.md. Import in compositions to get MIDI program,
range zones, registrations, articulations and synthesis defaults.
"""

MIDI_PROGRAM = 17
GM_NAME = "Percussive Organ"
# RenderPipeline stem label: GM_PROGRAMS[17] = "Percussive Organ" ->
# trackXX_Percussive_Organ.wav (labels match exactly, no quirk).
STEM_LABEL = "Percussive_Organ"

# MIDI ranges (sounding pitch, non-transposing). 61-key manual.
RANGE_MIN = 36       # C2 — bottom of the manual / left-hand key bass
RANGE_MAX = 96       # C7 — top of the manual
SOLO_RANGE = (48, 84)   # C3–C6 — right-hand comp/lead register
SWEET_SPOT = (52, 84)   # E3–C6 — percussion ping cuts, body stays warm

# Register zones
ZONES = {
    "bass": (36, 55),    # C2–G3 — left-hand key bass, 16'+8', percussion OFF
    "mid": (56, 79),     # G#3–G5 — primary comp register, percussion 3rd
    "high": (80, 96),    # G#5–C7 — funk stabs, percussion 2nd, solos
}

# Articulation defaults (velocity, duration_factor). Velocity is an AMPLITUDE
# value on the FluidR3 patch (centroid is constant 1.37–1.43 kHz from vel 20
# to 127 — measured), so accents need real velocity, not "harder playing".
ARTICULATIONS = {
    "sustain": (82, 1.0),      # held chord, flat body under the ping
    "stab": (96, 0.18),        # the funk/soul rhythm cell — percussion leads
    "chop": (74, 0.09),        # key-click + percussion only, almost no body
    "percussion": (92, 0.30),  # key-on 3rd-harmonic ping, body ducked
    "key_click": (70, 0.05),   # busbar transient, no tone
    "accent": (104, 0.80),     # downbeat with full drawbars + percussion
    "swell": (94, 1.0),        # pedal swell on a sustained chord
    "smear": (64, 0.90),       # chromatic smear / glissando fill
}

# Synthesis engine recommendation
SYNTHESIS = "additive"     # sound/synthesis/additive.py (SoundWave)

# Nine drawbars, console order: label -> harmonic ratio vs 8' (1.0).
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

# Registrations as nine levels 0-8 (console order above). Percussive-organ
# registrations are BRIGHTER and THINNER than the Drawbar Organ's: the
# percussion tab supplies the transient, so the sustain stops stay lean.
DRAWBAR_PRESETS = {
    "perc3": (8, 8, 8, 0, 0, 0, 0, 0, 0),   # 888 + 3rd percussion — the default
    "perc2": (8, 8, 8, 0, 0, 0, 0, 0, 0),   # 888 + 2nd percussion (same bars)
    "funk": (8, 8, 8, 6, 0, 0, 0, 0, 0),    # bright comp with 4' bite
    "gospel": (8, 8, 8, 8, 6, 0, 0, 0, 0),  # full scream when pushed
    "jazz": (8, 6, 8, 4, 0, 0, 0, 0, 0),    # Jimmy Smith club comp
    "soul": (8, 0, 8, 4, 0, 0, 0, 0, 0),    # Booker T. single-stop comp
    "bass": (8, 0, 8, 0, 0, 0, 0, 0, 0),    # left-hand/pedal roots, perc OFF
    "ballad": (0, 0, 8, 0, 0, 0, 0, 0, 0),  # 8' only, percussion OFF
}

# Percussion tab model: one fast-decaying partial added on key-on.
# harmonic 3 (2 2/3') is the classic "ping"; 2 (4') is brighter/deeper.
PERCUSSION_DEFAULTS = {
    "harmonic": 3,          # 3 = 2 2/3' ping (default), 2 = 4' ping
    "level": 0.45,          # relative to the sustain bank (0–1)
    "decay_s": 0.18,        # 80 ms (fast) … 400 ms (slow) on the real tab
    "decay_setting": "fast",
    "key_click_level": 0.10,
    "key_click_ms": 4.0,
}

# Engine-compatible integer-partial banks (the additive engine normalizes the
# sum to 1.0). Percussive-organ banks carry less 4x/6x/8x than the Rock Organ
# banks but MORE 3x — the percussion ping is a 3rd harmonic.
ADDITIVE_HARMONICS = {
    # partials:  1x     2x     3x     4x     5x     6x     7x     8x
    "perc3":  [1.00, 0.55, 0.75, 0.30, 0.08, 0.04, 0.00, 0.02],
    "perc2":  [1.00, 0.85, 0.40, 0.35, 0.06, 0.03, 0.00, 0.02],
    "funk":   [1.00, 0.60, 0.70, 0.45, 0.15, 0.06, 0.00, 0.04],
    "gospel": [1.00, 0.80, 0.85, 0.60, 0.30, 0.15, 0.05, 0.10],
    "jazz":   [1.00, 0.50, 0.55, 0.28, 0.06, 0.03, 0.00, 0.00],
    "soul":   [1.00, 0.35, 0.30, 0.18, 0.04, 0.00, 0.00, 0.00],
    "bass":   [1.00, 0.45, 0.00, 0.12, 0.00, 0.00, 0.00, 0.00],
    "ballad": [1.00, 0.15, 0.00, 0.03, 0.00, 0.00, 0.00, 0.00],
}

# ADSR for the native additive path. Contact closure is fast; the percussion
# ping is a SEPARATE short envelope (PERCUSSION_DEFAULTS), not part of ADSR.
ADDITIVE_ENVELOPE = {
    "attack": 0.004,     # s — busbar contact
    "decay": 0.0,        # s — tonewheel output is flat while held
    "sustain": 1.0,
    "release": 0.040,    # s — key-off cut + click
}

# Measured FluidR3_GM.sf2 behaviour of bank-0 preset 17 (see instrument.md).
# The SF2 patch is NOT a flat-sustain organ: the body swells for ~150–250 ms
# and then decays a few dB, with a slow amplitude wobble from the preset's
# chorus/rotary. Native additive synthesis does not need this; it is here so
# arrangements written for the SF2 render keep their staccato notes long
# enough to be heard.
SF2_ENVELOPE = {
    "swell_ms": (150, 250),   # time to full body (measured, vel 100)
    "swell_db": 9.0,          # body level at 20 ms vs peak
    "decay_db_per_s": 5.0,    # slow post-swell decay while key is held
    "wobble_hz": 0.7,         # preset chorus/rotary amplitude wobble
    "wobble_db": 2.0,
}

# PhaseModSynth alternative (cheap FM percussive organ). A 2:1 or 3:1 ratio
# with a short modulation decay approximates the key-on ping; there is no
# drawbar mixing in the FM path, so it is a stand-in only.
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.0,   # 3rd-harmonic ping (use 2.0 for the 4' tab)
    "mod_depth": 2.4,
    "mod_decay_s": 0.18,     # percussion tab decay
    "attack": 0.004,
    "release": 0.04,
}

# Production defaults
REVERB_TAIL = 1.6        # seconds — club/stage ambience; shorter than church
EQ_BODY = (300, -1.0)    # peaking cut Hz, dB — clear 16' mud under the ping
EQ_PRESENCE = (2500, 2.5)  # peaking boost Hz, dB — the percussion ping band
EQ_AIR = (8000, 1.5)     # highshelf Hz, dB — key click + drawbar top
PAN = 0.0                # centre; ±0.25 when doubled with a clean organ


def drawbar_harmonics(registration=DRAWBAR_PRESETS["perc3"]):
    """Map a nine-level drawbar registration to {harmonic_ratio: gain}.

    Levels are 0-8 on the console; gain is level/8 (linear busbar mixing).
    Ratios include the 0.5x sub-octave (16') and 1.5x quint (5 1/3').
    """
    out = {}
    for (label, ratio), level in zip(DRAWBAR_FOOTAGES, registration):
        if level:
            out[ratio] = round(level / 8.0, 4)
    return out


def percussion_envelope(duration_s=0.18, sample_rate=44100.0):
    """Exponential decay envelope for the key-on percussion ping.

    Returns a numpy array peaking at 1.0 on the first sample, ~-60 dB at
    ``duration_s``. The real tab decays 80–400 ms; 180 ms is the 'fast' stop.
    """
    import numpy as np
    n = max(2, int(duration_s * sample_rate))
    t = np.arange(n) / sample_rate
    return np.exp(-6.9 * t / max(duration_s, 1e-3))


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
