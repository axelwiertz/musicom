# -*- coding: utf-8 -*-
"""Voice-like family — shared manufacturing constants.

Six synthesized instruments that sound *familiar like a human voice* without
being voices. Each has its own non-vocal physical excitation (free reed,
mirliton membrane, plucked lamella, lip reed, bowed steel, amplified saw),
routed through a vocal-tract formant cascade. The engine lives in
sound/synthesis/voice_like.py.

The common thread (Fant 1960, source-filter theory): vocal familiarity lives
in the **formant envelope**, not in the vocal folds. That is why a pipe organ
stop made of reed pipes has been called *vox humana* since the 16th century.

No GM preset reproduces these — a soundfont "voice" is a sampled choir. These
are SYNTHESIS instruments: compositions route them to VoiceLikeInstrument,
not FluidSynth. The MIDI programs below exist only so the parts are
identifiable on export.
"""

#: key -> (label, GM program, GM name, stem label, range, sweet spot, engine key)
FAMILY = {
    "vox_humana": dict(
        label="Vox Humana", midi_program=20, gm_name="Reed Organ",
        stem_label="Reed_Organ", range=(48, 84), sweet_spot=(55, 79),
        engine="vox_humana",
        desc="Free reed + very short resonator; the organ stop named for the voice.",
    ),
    "kazoo": dict(
        label="Kazoo", midi_program=59, gm_name="Muted Trumpet",
        stem_label="Muted_Trumpet", range=(50, 86), sweet_spot=(57, 81),
        engine="kazoo",
        desc="Mirliton membrane buzz — colours whatever is sung into it.",
    ),
    "jaw_harp": dict(
        label="Jaw Harp", midi_program=106, gm_name="Shamisen",
        stem_label="Shamisen", range=(36, 74), sweet_spot=(45, 69),
        engine="jaw_harp",
        desc="Plucked lamella; the mouth cavity selects one overtone.",
    ),
    "didgeridoo": dict(
        label="Didgeridoo", midi_program=20, gm_name="Reed Organ",
        stem_label="Reed_Organ", range=(24, 55), sweet_spot=(28, 50),
        engine="didgeridoo",
        desc="Lip reed into a long bore; mouth formants shape the drone.",
    ),
    "singing_saw": dict(
        label="Singing Saw", midi_program=81, gm_name="Lead 2 (sawtooth)",
        stem_label="Lead_2_sawtooth", range=(55, 91), sweet_spot=(60, 84),
        engine="singing_saw",
        desc="Bowed steel blade: friction tone with a wide vocal vibrato.",
    ),
    "talkbox": dict(
        label="Talkbox", midi_program=80, gm_name="Lead 1 (square)",
        stem_label="Lead_1_square", range=(45, 84), sweet_spot=(52, 79),
        engine="talkbox",
        desc="Instrument driven through the player's mouth — the mouth IS the filter.",
    ),
}

#: One representative instrument for the registry's `voice_like` slot. The
#: family is exposed as a *group*; pick a member with VoiceLikeInstrument(key).
DEFAULT_KEY = "vox_humana"
_D = FAMILY[DEFAULT_KEY]

MIDI_PROGRAM = _D["midi_program"]
GM_NAME = _D["label"]
STEM_LABEL = _D["stem_label"]

RANGE_MIN, RANGE_MAX = _D["range"]
SOLO_RANGE = _D["sweet_spot"]
SWEET_SPOT = _D["sweet_spot"]

ZONES = {
    "low": (_D["range"][0], _D["range"][0] + 12),
    "mid": (_D["sweet_spot"][0], _D["sweet_spot"][1]),
    "high": (_D["sweet_spot"][1], _D["range"][1]),
}

# Articulations map to engine parameters (vowel, vibrato, breath):
# (vowel, vibrato_depth_semitones, noise_scale)
ARTICULATIONS = {
    "legato":   ("a", 0.32, 1.0),
    "open":     ("o", 0.30, 1.0),
    "bright":   ("i", 0.28, 1.0),
    "dark":     ("u", 0.34, 1.2),
    "nasal":    ("e", 0.30, 1.0),
    "tremulant": ("a", 0.55, 0.8),   # organ tremulant / heavy vibrato
}

# Synthesis engine recommendation.
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


def midi_to_freq(midi: int) -> float:
    """Standard MIDI to Hz conversion."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
