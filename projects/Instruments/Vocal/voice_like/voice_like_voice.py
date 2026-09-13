# -*- coding: utf-8 -*-
"""Voice-like family — six individual voice-adjacent instruments.

Each of these is a *non-vocal* instrument that sounds familiar like a human
voice: a free reed, a mirliton membrane, a plucked lamella, a lip reed, a
bowed steel blade, an amplified saw — each routed through a vocal-tract formant
cascade. The engine lives in sound/synthesis/voice_like.py.

The common thread (Fant 1960, source-filter theory): vocal familiarity lives
in the **formant envelope**, not in the vocal folds. That is why a pipe organ
stop made of reed pipes has been called *vox humana* since the 16th century.

Each member registers under its own key so a composition can pick one for a
track (``by_name("kazoo")``). ``GM_NAME`` here is the FluidSynth stand-in used
for MIDI export only — the actual audio always comes from VoiceLikeInstrument,
never the soundfont.
"""

#: key -> (label, GM program, GM stand-in name, stem label, range, sweet spot)
MEMBERS = {
    "vox_humana": dict(
        label="Vox Humana", program=20, gm="Reed Organ", stem="Reed_Organ",
        rng=(48, 84), sweet=(55, 79),
        desc="Free reed + very short resonator; the organ stop named for the voice.",
    ),
    "kazoo": dict(
        label="Kazoo", program=59, gm="Muted Trumpet", stem="Muted_Trumpet",
        rng=(50, 86), sweet=(57, 81),
        desc="Mirliton membrane buzz — colours whatever is sung into it.",
    ),
    "jaw_harp": dict(
        label="Jaw Harp", program=106, gm="Shamisen", stem="Shamisen",
        rng=(36, 74), sweet=(45, 69),
        desc="Plucked lamella; the mouth cavity selects one overtone.",
    ),
    "didgeridoo": dict(
        label="Didgeridoo", program=20, gm="Reed Organ", stem="Reed_Organ",
        rng=(24, 55), sweet=(28, 50),
        desc="Lip reed into a long bore; mouth formants shape the drone.",
    ),
    "singing_saw": dict(
        label="Singing Saw", program=81, gm="Lead 2 (sawtooth)", stem="Lead_2_sawtooth",
        rng=(55, 91), sweet=(60, 84),
        desc="Bowed steel blade: friction tone with a wide vocal vibrato.",
    ),
    "talkbox": dict(
        label="Talkbox", program=80, gm="Lead 1 (square)", stem="Lead_1_square",
        rng=(45, 84), sweet=(52, 79),
        desc="Instrument driven through the player's mouth — the mouth IS the filter.",
    ),
}

# The family umbrella. `voice_like` resolves to its most representative member
# (vox humana) for backwards compatibility; each member is also individually
# registered via `voice_like_<key>`.
DEFAULT_KEY = "vox_humana"
_D = MEMBERS[DEFAULT_KEY]

MIDI_PROGRAM = _D["program"]
GM_NAME = _D["label"]
STEM_LABEL = _D["stem"]

RANGE_MIN, RANGE_MAX = _D["rng"]
SOLO_RANGE = _D["sweet"]
SWEET_SPOT = _D["sweet"]

ZONES = {
    "low": (_D["rng"][0], _D["rng"][0] + 12),
    "mid": (_D["sweet"][0], _D["sweet"][1]),
    "high": (_D["sweet"][1], _D["rng"][1]),
}

# Articulations map to engine parameters (vowel, vibrato, breath):
# (vowel, vibrato_depth_semitones, noise_scale)
ARTICULATIONS = {
    "legato":     ("a", 0.32, 1.0),
    "open":       ("o", 0.30, 1.0),
    "bright":     ("i", 0.28, 1.0),
    "dark":       ("u", 0.34, 1.2),
    "nasal":      ("e", 0.30, 1.0),
    "tremulant":  ("a", 0.55, 0.8),   # organ tremulant / heavy vibrato
}

# Synthesis engine recommendation (shared by all six).
SYNTHESIS = "voice_like"      # sound/synthesis/voice_like.py VoiceLikeInstrument

SYNTHESIS_DEFAULTS = {
    "instrument": DEFAULT_KEY,
    "sample_rate": 44100,
    "vowel": "a",
    "seed": 0,
}

# Production defaults (organ-stop-like: small room, no long tail).
REVERB_TAIL = 1.3
EQ_BODY = (500, -2.0)     # cut Hz, dB — hollower "short resonator" character
EQ_PRESENCE = (2800, 2.0)  # boost Hz, dB — the formant ring that reads as voice
EQ_AIR = (7000, 1.0)      # highshelf Hz, dB
PAN = 0.0

#: The full family, keyed by registry key. instrument_registry reads `FAMILY`
#: and registers each member as an individual instrument (so compositions can
#: pick ``by_name("kazoo")`` etc.). Fields map onto Instrument attributes:
#: label → human name / gm_name, engine → synthesis engine key.
FAMILY = {
    key: {
        "label": v["label"], "midi_program": v["program"], "stem_label": v["stem"],
        "range_min": v["rng"][0], "range_max": v["rng"][1],
        "sweet_spot": v["sweet"], "engine": key,
    }
    for key, v in MEMBERS.items()
}


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
