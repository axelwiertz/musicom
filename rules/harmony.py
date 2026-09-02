# -*- coding: utf-8 -*-
"""Canonical harmony tables — single source of truth.

Consolidates the KEY_OFFSET / CHORD_SHAPES / QUALITY_INTERVALS /
MAJOR_DEGREES / PROGRESSIONS tables that used to be duplicated across:

    workflows/paths.py          (had the fullest version)
    workflows/musicom_workflow.py (local divergent copy)
    generators/tonal_network.py (CHORD_QUALITY — same data as QUALITY_INTERVALS)

Import from here everywhere; do NOT redefine these tables elsewhere.
"""

from typing import Dict, List, Tuple

# Diatonic chord shapes: degree -> (root_interval, quality)
CHORD_SHAPES = {
    "I": (0, "maj"), "ii": (2, "min"), "iii": (4, "min"),
    "IV": (5, "maj"), "V": (7, "maj"), "vi": (9, "min"), "vii": (11, "dim"),
}

# Major scale degree names, in order
MAJOR_DEGREES = ["I", "ii", "iii", "IV", "V", "vi", "vii"]

# Key name -> semitone offset from C (both major and relative-minor spellings)
KEY_OFFSET = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
    "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
    "A#": 10, "Bb": 10, "B": 11,
    # relative minor keys
    "Cm": -3, "C#m": -2, "Dm": -1, "D#m": 0, "Em": 1, "Fm": 2,
    "F#m": 3, "Gm": 4, "G#m": 5, "Am": 6, "A#m": 7, "Bm": 8,
}

# Common progressions by style flavor (degree lists)
PROGRESSIONS = {
    "pop": ["I", "V", "vi", "IV"],
    "pop-ballad": ["I", "vi", "IV", "V"],
    "andalucian": ["i", "VII", "VI", "V"],  # flamenco flavor
    "doo-wop": ["I", "vi", "IV", "V"],
    "minor-aeolian": ["i", "VI", "III", "VII"],
    "major-asc": ["I", "III", "IV", "V"],
    "blues-rock": ["I", "IV", "I", "V"],
}

# Chord quality -> semitone offsets from root.
# Short names (maj/min/dim) are canonical; long names (major/minor/diminished,
# dominant7) are aliases used by generators/tonal_network.py.
QUALITY_INTERVALS = {
    "maj": (0, 4, 7),
    "min": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "maj7": (0, 4, 7, 11),
    "dom7": (0, 4, 7, 10),
    "min7": (0, 3, 7, 10),
    "half_dim7": (0, 3, 6, 10),
    "dim7": (0, 3, 6, 9),
    # long-name aliases
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "diminished": (0, 3, 6),
    "augmented": (0, 4, 8),
    "dominant7": (0, 4, 7, 10),
}

# Major scale offsets per degree index (for a C root)
_MAJOR_SCALE_OFFSETS = [0, 2, 4, 5, 7, 9, 11]
# Natural-minor spelling offsets per degree index (b3, b6, b7)
_MINOR_SCALE_OFFSETS = [0, 2, 3, 5, 7, 8, 10]


def chord_tones(degree: str, root_midi: int) -> List[int]:
    """Pitch classes of a chord built on `root_midi` for a scale degree.

    Handles both "I"/"vi" (major scale spelling) and "i"/"VII" (natural
    minor spelling, flamenco-style) by case: uppercase roots follow the
    major scale offsets, lowercase follow the natural minor scale.
    """
    qual = "maj" if degree == degree.upper() else "min"
    letter = degree.upper()
    if letter in MAJOR_DEGREES:
        idx = MAJOR_DEGREES.index(letter)
        scale_off = (_MINOR_SCALE_OFFSETS if degree != degree.upper()
                     else _MAJOR_SCALE_OFFSETS)[idx]
    else:
        scale_off = 0
    root = root_midi + scale_off
    intervals = QUALITY_INTERVALS[qual]
    return [root + i for i in intervals]
