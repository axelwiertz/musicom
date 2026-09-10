# -*- coding: utf-8 -*-
"""Canonical harmony tables — single source of truth.

Consolidates the KEY_OFFSET / CHORD_SHAPES / QUALITY_INTERVALS /
MAJOR_DEGREES / PROGRESSIONS tables that used to be duplicated across:

    workflows/paths.py          (had the fullest version)
    workflows/musicom_workflow.py (local divergent copy)
    generators/tonal_network.py (CHORD_QUALITY — same data as QUALITY_INTERVALS)

Import from here everywhere; do NOT redefine these tables elsewhere.
"""

from typing import Dict, List, Optional, Tuple

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


# --- Roman-numeral parsing (mode-aware degree -> semitone offset) -----------
# Scale-degree index for the seven roman numerals, case-insensitive.
_DEGREE_ROMAN = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6}

# Semitone offsets per scale-degree index, by mode.
MODE_OFFSETS = {
    "major": (0, 2, 4, 5, 7, 9, 11),   # ionian
    "minor": (0, 2, 3, 5, 7, 8, 10),   # aeolian / natural minor (b3, b6, b7)
}

MINOR_TONICS = frozenset({"i"})


def parse_degree(degree: str) -> Tuple[int, int]:
    """(scale_degree_index, accidental) for a roman-numeral symbol.

    Accepts case variants ("I"/"i"), leading accidentals ("bVII", "#IV",
    "bVI"), and quality/extension suffixes ("ii°", "viio", "V7", "iv6").
    Returns the 0-based degree index (0 = tonic) and the accidental in
    semitones (-1 flat, +1 sharp, 0 natural). Raises ValueError otherwise.
    """
    import re
    if not isinstance(degree, str) or not degree.strip():
        raise ValueError(f"bad degree {degree!r}")
    m = re.match(r"^\s*([b#]?)\s*([iIvV]+)", degree)
    if not m:
        raise ValueError(f"unparseable degree {degree!r}")
    acc_sym, roman = m.group(1), m.group(2).upper()
    idx = _DEGREE_ROMAN.get(roman)
    if idx is None:
        raise ValueError(f"unknown degree {degree!r}")
    acc = {"b": -1, "#": 1}.get(acc_sym, 0)
    return idx, acc


def degree_offset(degree: str, mode: str = "major") -> int:
    """Semitone offset of a scale degree above the tonic for `mode`.

    This is the mode-aware replacement for the historical
    `MAJOR_DEGREES.index(deg.upper())` lookup, which collapsed every
    uppercase minor-mode degree (VI/III/VII) and every lowercase
    major-mode degree (ii/iii/vi/vii) onto index 0 — producing static,
    all-tonic harmony for minor-key progressions.
    """
    if mode not in MODE_OFFSETS:
        raise ValueError(f"mode must be one of {sorted(MODE_OFFSETS)}, got {mode!r}")
    idx, acc = parse_degree(degree)
    base = MODE_OFFSETS[mode][idx]
    if mode == "minor":
        # The aeolian table already carries b3/b6/b7, so an explicit flat on
        # VI/III/VII is the same degree (bIII == III). Sharps still apply
        # (e.g. #VII = harmonic-minor leading tone).
        return base + (acc if acc > 0 else 0)
    return base + acc


def infer_mode(key: str, progression=None) -> str:
    """Resolve 'major'/'minor' from a key name and/or a progression.

    Precedence: explicit 'm' suffix on the key ("Dm", "Am") > a lowercase
    tonic 'i' anywhere in the progression (aeolian convention) > major.

    Scanning the whole progression (not just its first degree) matters for
    progressions that begin off-tonic, e.g. a bridge on VII-VI-III-VII.
    """
    if isinstance(key, str) and key.endswith("m") and (
            key[:-1] in KEY_OFFSET):
        return "minor"
    if progression:
        if any(str(d).strip() in MINOR_TONICS for d in progression):
            return "minor"
    return "major"


def tonic_offset(key: str) -> int:
    """Semitone offset of the key's tonic from C (mode-independent).

    Minor spellings ("Dm") resolve to their tonic letter ("D" -> 2), since
    KEY_OFFSET's relative-minor entries encode a different (legacy)
    convention.
    """
    if isinstance(key, str) and key.endswith("m") and key[:-1] in KEY_OFFSET:
        return KEY_OFFSET[key[:-1]]
    return KEY_OFFSET.get(key, 0)


def progression_roots(progression, total_bars: int, key: str,
                      harmonic_rhythm: int = 1, mode: Optional[str] = None,
                      base_octave: int = 36) -> List[int]:
    """Root MIDI pitches for `progression` tiled over `total_bars` bars.

    harmonic_rhythm = bars per chord (1 = change every bar, 2 = every other
    bar). Roots land in the C2-C3 octave by default (36-48), matching the
    engine's historical convention.
    """
    if not progression:
        raise ValueError("empty progression")
    mode = mode or infer_mode(key, progression)
    off = tonic_offset(key)
    return [base_octave + off + degree_offset(
                progression[(b // harmonic_rhythm) % len(progression)], mode)
            for b in range(total_bars)]


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
