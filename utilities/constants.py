"""Musical constants and enumerations for musicom."""

from typing import Dict, List, Tuple

# Pitch Classes
PITCH_CLASSES: List[str] = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Enharmonic equivalents
ENHARMONIC_MAP: Dict[str, str] = {
    'Db': 'C#',
    'Eb': 'D#',
    'Fb': 'E',
    'E#': 'F',
    'Gb': 'F#',
    'Ab': 'G#',
    'Bb': 'A#',
    'Cb': 'B',
    'B#': 'C',
}

# Interval names (semitones to interval name)
INTERVAL_NAMES: Dict[int, str] = {
    0: 'P1',   # Perfect unison
    1: 'm2',   # Minor second
    2: 'M2',   # Major second
    3: 'm3',   # Minor third
    4: 'M3',   # Major third
    5: 'P4',   # Perfect fourth
    6: 'TT',   # Tritone
    7: 'P5',   # Perfect fifth
    8: 'm6',   # Minor sixth
    9: 'M6',   # Major sixth
    10: 'm7',  # Minor seventh
    11: 'M7',  # Major seventh
    12: 'P8',  # Perfect octave
}

# Interval qualities
INTERVAL_QUALITIES: Dict[str, str] = {
    'P': 'Perfect',
    'M': 'Major',
    'm': 'minor',
    'A': 'Augmented',
    'd': 'diminished',
}

# Scale patterns (semitone intervals from tonic)
SCALE_PATTERNS: Dict[str, List[int]] = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'natural_minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
    'aeolian': [0, 2, 3, 5, 7, 8, 10],  # Same as natural minor
    'ionian': [0, 2, 4, 5, 7, 9, 11],   # Same as major
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'whole_tone': [0, 2, 4, 6, 8, 10],
    'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}

# Chord qualities (intervals from root)
CHORD_QUALITIES: Dict[str, List[int]] = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'major7': [0, 4, 7, 11],
    'minor7': [0, 3, 7, 10],
    'dominant7': [0, 4, 7, 10],
    'diminished7': [0, 3, 6, 9],
    'half_diminished7': [0, 3, 6, 10],
    'minor_major7': [0, 3, 7, 11],
    'augmented7': [0, 4, 8, 10],
    'major6': [0, 4, 7, 9],
    'minor6': [0, 3, 7, 9],
    'major9': [0, 4, 7, 11, 14],
    'minor9': [0, 3, 7, 10, 14],
    'dominant9': [0, 4, 7, 10, 14],
    'major11': [0, 4, 7, 11, 14, 17],
    'minor11': [0, 3, 7, 10, 14, 17],
    'dominant11': [0, 4, 7, 10, 14, 17],
    'major13': [0, 4, 7, 11, 14, 17, 21],
    'minor13': [0, 3, 7, 10, 14, 17, 21],
    'dominant13': [0, 4, 7, 10, 14, 17, 21],
}

# Roman numeral to scale degree
ROMAN_NUMERALS: Dict[str, int] = {
    'I': 1, 'i': 1,
    'II': 2, 'ii': 2,
    'III': 3, 'iii': 3,
    'IV': 4, 'iv': 4,
    'V': 5, 'v': 5,
    'VI': 6, 'vi': 6,
    'VII': 7, 'vii': 7,
}

# Harmonic functions
HARMONIC_FUNCTIONS: Dict[str, str] = {
    'I': 'tonic',
    'ii': 'subdominant',
    'iii': 'tonic',
    'IV': 'subdominant',
    'V': 'dominant',
    'vi': 'tonic',
    'vii°': 'dominant',
}

# Default values
DEFAULT_TEMPO: float = 120.0
DEFAULT_TIME_SIGNATURE: Tuple[int, int] = (4, 4)
DEFAULT_VELOCITY: int = 64
DEFAULT_OCTAVE: int = 4

# MIDI ranges
MIDI_RANGE: Tuple[int, int] = (0, 127)
VELOCITY_RANGE: Tuple[int, int] = (0, 127)

# Note durations (in quarter notes)
NOTE_DURATIONS: Dict[str, float] = {
    'whole': 4.0,
    'half': 2.0,
    'quarter': 1.0,
    'eighth': 0.5,
    'sixteenth': 0.25,
    'thirty_second': 0.125,
    'sixty_fourth': 0.0625,
    'dotted_half': 3.0,
    'dotted_quarter': 1.5,
    'dotted_eighth': 0.75,
    'triplet_quarter': 2.0 / 3.0,
    'triplet_eighth': 1.0 / 3.0,
}

# Articulation types
ARTICULATIONS: List[str] = [
    'staccato',
    'staccatissimo',
    'tenuto',
    'accent',
    'marcato',
    'fermata',
    'legato',
]

# Dynamic markings
DYNAMICS: List[str] = [
    'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff',
    'sfz', 'fp', 'crescendo', 'diminuendo',
]

# Tempo markings
TEMPO_MARKINGS: Dict[str, Tuple[int, int]] = {
    'grave': (25, 45),
    'largo': (40, 60),
    'lento': (45, 60),
    'adagio': (55, 75),
    'andante': (76, 108),
    'moderato': (108, 120),
    'allegretto': (112, 120),
    'allegro': (120, 168),
    'vivace': (168, 176),
    'presto': (168, 200),
    'prestissimo': (200, 240),
}
