"""Twelve tone equal temperament: Chromatic pitches in helix structure."""
import numpy as np
from dataclasses import dataclass
from librosa import midi_to_hz, midi_to_note

"""Twelve-tone equal temperament constants and pitch class definitions"""

""" TODO: Add
Equal‑tempered constants
12‑TET interval ratios
Equal temperament ratios
Semitone ratio (for the base constant: 2^(1/12))
Twelfth‑root‑of‑2 constant
Step ratio (12‑tone equal temperament)
Equal‑tempered step size
Pitch‑class ratios (12‑TET)
Frequency ratio for a semitone
Log‑frequency increment (12‑TET)
"""

@dataclass(frozen=True)
class MusicPitchClass:
    # Pitch class numbers and names
    C = 0
    C_SHARP = D_FLAT = 1
    D = 2
    D_SHARP = E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = G_FLAT = 6
    G = 7
    G_SHARP = A_FLAT = 8
    A = 9
    A_SHARP = B_FLAT = 10
    B = 11
    # 12-tone pitch class numbers and names
    NUMBERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NAMES_FLATMAP = {'D': 'C#', 'E': 'D#', 'F': 'E', 'G': 'F#', 'A': 'G#', 'B': 'A#', 'C': 'B'}
    NAMES_SHARPMAP = {v: k for k, v in NAMES_FLATMAP.items()}

    SIZE : int = len(NUMBERS)

    @classmethod
    def size(cls) -> int:
        """Return the number of pitch classes (12)."""
        return len(cls.NUMBERS)

    @classmethod
    def number_of(cls, name: str) -> int:
        """Return the pitch class number (0-11) for a given name."""
        if name in cls.NAMES_SHARP:
            return cls.NAMES_SHARP.index(name)
        elif name in cls.NAMES_FLATMAP:
            sharp_name = cls.NAMES_FLATMAP[name]
            return cls.NAMES_SHARP.index(sharp_name)
        else:
            raise ValueError(f"Invalid pitch class name: {name}")

    @classmethod
    def name_of(cls, pitch_class: int, use_flats: bool = False) -> str:
        """Return the name of a pitch class (0-11)."""
        if not (0 <= pitch_class < cls.size()):
            raise ValueError(f"Pitch class must be in range 0-{cls.SIZE-1}")
        name = cls.NAMES_SHARP[pitch_class]
        if use_flats and name in cls.NAMES_FLATMAP.values():
            # Convert to flat name
            for flat_name, sharp_name in cls.NAMES_FLATMAP.items():
                if sharp_name == name:
                    return flat_name
        return name

@dataclass(frozen=True)
class MusicOctave:
    MIN = -1  # Lowest octave (C-1)
    MAX = 9   # Highest octave (G9)
@dataclass(frozen=True)
class Direction:
    ASCENDING = 1
    DESCENDING = -1

"""Chromatic pitch grid """
class MusicPitchGrid:
    MIDI_MIN = 0    # Lowest MIDI note
    MIDI_MAX = 127  # Highest MIDI note
    CENTS: float = 100  # Cents in semitone

    def __init__(self, midi_pitches: np.ndarray | list | None = None):
        """
        Initialize MusicPitchGrid with MIDI pitch numbers.

        Args:
            midi_pitches: Array of MIDI note numbers (0-127).
                          If None, creates full chromatic range (0-127).
        """
        if midi_pitches is None:
            # Default: full MIDI range
            self._midi_pitches = np.arange(self.MIDI_MIN, self.MIDI_MAX + 1, dtype=np.int8)
        else:
            self._midi_pitches = np.asarray(midi_pitches, dtype=np.int8)
            # Validate range
            if np.any((self._midi_pitches < self.MIDI_MIN) | (self._midi_pitches > self.MIDI_MAX)):
                raise ValueError(f"MIDI pitches must be in range {self.MIDI_MIN}-{self.MIDI_MAX}")

    def __len__(self) -> int:
        return len(self._midi_pitches)

    def __getitem__(self, idx) -> int:
        """Get MIDI pitch at index."""
        return int(self._midi_pitches[idx])

    def __iter__(self):
        return iter(self._midi_pitches)

    @property
    def midi_array(self) -> np.ndarray:
        """Return the underlying MIDI pitch array."""
        return self._midi_pitches.copy()

    @property
    def frequencies(self) -> np.ndarray:
        """Return frequencies (Hz) for all pitches using librosa."""
        return midi_to_hz(self._midi_pitches.astype(float))

    @property
    def names(self) -> list[str]:
        """Return note names for all pitches using librosa."""
        return [midi_to_note(int(m)) for m in self._midi_pitches]

    def transpose(self, interval_steps: int, direction: int = Direction.ASCENDING) -> 'MusicPitchGrid':
        """
        Transpose all pitches by interval_steps in direction.
        Returns a new MusicPitchGrid instance.
        """
        transposed = self._midi_pitches + (direction * interval_steps)
        # Clip to valid MIDI range
        transposed = np.clip(transposed, self.MIDI_MIN, self.MIDI_MAX)
        return MusicPitchGrid(transposed)

    def octave_of(self, idx: int) -> int:
        """Return octave number for pitch at given index (MIDI octave convention)."""
        midi = self._midi_pitches[idx]
        return int(midi // MusicPitchClass.SIZE) - 1

    def pitch_class_of(self, idx: int) -> int:
        """Return pitch class number (0-11) for pitch at given index."""
        return int(self._midi_pitches[idx] % MusicPitchClass.SIZE)

    def midi_at(self, idx: int) -> int:
        """Return MIDI note number at given index."""
        return int(self._midi_pitches[idx])

    def freq_at(self, idx: int) -> float:
        """Return frequency (Hz) for pitch at given index."""
        return float(midi_to_hz(float(self._midi_pitches[idx])))

    def name_at(self, idx: int) -> str:
        """Return note name for pitch at given index."""
        return midi_to_note(int(self._midi_pitches[idx]))

    def get_at(self, idx: int) -> tuple[int, int]:
        """Get (pitch_class, octave) at index idx."""
        midi = self._midi_pitches[idx]
        return int(midi % MusicPitchClass.SIZE), int(midi // MusicPitchClass.SIZE) - 1

    def index_of_midi(self, midi: int) -> int | None:
        """Return index of given MIDI note, or None if not present."""
        indices = np.where(self._midi_pitches == midi)[0]
        return int(indices[0]) if len(indices) > 0 else None

    def index_of(self, pitch_class: int, octave: int) -> int | None:
        """Return index for a given pitch class and octave, or None if not present."""
        midi = (octave + 1) * MusicPitchClass.SIZE + pitch_class
        return self.index_of_midi(midi)

    def filter_by_pitch_class(self, pitch_classes: list[int]) -> 'MusicPitchGrid':
        """Return new MusicPitchGrid containing only pitches with given pitch classes."""
        mask = np.isin(self._midi_pitches % MusicPitchClass.SIZE, pitch_classes)
        return MusicPitchGrid(self._midi_pitches[mask])

    def filter_by_octave(self, octaves: list[int]) -> 'MusicPitchGrid':
        """Return new MusicPitchGrid containing only pitches in given octaves."""
        midi_octaves = (self._midi_pitches // MusicPitchClass.SIZE) - 1
        mask = np.isin(midi_octaves, octaves)
        return MusicPitchGrid(self._midi_pitches[mask])

    def filter_by_range(self, midi_min: int, midi_max: int) -> 'MusicPitchGrid':
        """Return new MusicPitchGrid containing only pitches in MIDI range."""
        mask = (self._midi_pitches >= midi_min) & (self._midi_pitches <= midi_max)
        return MusicPitchGrid(self._midi_pitches[mask])

    def show(self, radius: float = 1.0):
        """Visualize the pitches as a helix (imports Helix only when needed)."""
        from visualization import Helix

        # Create helix for visualization
        helix = Helix(MusicPitchClass.SIZE, MusicOctave.MAX-MusicOctave.MIN + 1)

        # Convert MIDI pitches to helix indices and plot
        helix.plot_3d(
            radius=radius,
            highlight_indices=[int(m) for m in self._midi_pitches]
        )

    @classmethod
    def from_range(cls, start_midi: int, end_midi: int) -> 'MusicPitchGrid':
        """Create MusicPitchGrid from a MIDI range (inclusive)."""
        return cls(np.arange(start_midi, end_midi + 1, dtype=np.int8))

    @classmethod
    def from_names(cls, names: list[str]) -> 'MusicPitchGrid':
        """Create MusicPitchGrid from a list of note names."""
        from librosa import note_to_midi
        midi_vals = [note_to_midi(n) for n in names]
        return cls(np.array(midi_vals, dtype=np.int8))


class MusicPitchRange:
    """ Pitch range defined by start and end pitches. """
    def __init__(self,
                pitch_start : tuple[MusicPitchClass, MusicOctave] = None,
                pitch_end : tuple[MusicPitchClass, MusicOctave] = None,
                 pitch_class_start: int = MusicPitchClass.A,
                 octave_start: int = 0,
                 pitch_class_end: int = MusicPitchClass.C,
                 octave_end: int = 8):

        # Calculate MIDI bounds
        if pitch_start is not None and pitch_end is not None:
            self.midi_start = pitch_start
            self.midi_end = pitch_end
        elif pitch_class_start is not None and pitch_class_end is not None:
            self.midi_start = (octave_start + 1) * MusicPitchClass.SIZE + pitch_class_start
            self.midi_end = (octave_end + 1) * MusicPitchClass.SIZE + pitch_class_end
        else:
            raise ValueError("Either pitch_start and pitch_end or pitch_class_start, octave_start, pitch_class_end, octave_end must be provided.")

    def __len__(self) -> int:
        return self.midi_end - self.midi_start + 1
