"""
Harmony generation module.

This module provides algorithms for generating chord progressions and voicings.
"""

from typing import List, Optional, Dict
import random

from musicom.ai.core.structures import Chord, Progression, Note
from musicom.ai.core.tet_system import Key, Scale
from musicom.ai.utils.constants import HARMONIC_FUNCTIONS
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('harmony')


class ProgressionGenerator:
    """Generate chord progressions."""

    def __init__(self, key: Key):
        """
        Initialize progression generator.

        Args:
            key: Key for the progression
        """
        self.key = key
        self.scale = key.get_scale()

    def generate_functional_progression(
        self,
        pattern: List[str],
        duration: float = 1.0,
        voicing_type: str = 'close',
        octave: int = 4
    ) -> Progression:
        """
        Generate progression from Roman numeral pattern.

        Args:
            pattern: List of Roman numerals (e.g., ['I', 'IV', 'V', 'I'])
            duration: Duration for each chord
            voicing_type: Voicing type ('close', 'open', 'root')
            octave: Base octave for chords

        Returns:
            Progression object
        """
        logger.info(f"Generating functional progression: {' - '.join(pattern)}")

        chords = []

        for roman in pattern:
            # Parse Roman numeral
            degree = self._parse_roman_numeral(roman)
            is_major = roman[0].isupper()

            # Get root from scale
            root = self.scale.get_degree(degree)

            # Determine chord quality
            if is_major:
                if '7' in roman:
                    quality = 'major7' if 'maj7' in roman else 'dominant7'
                else:
                    quality = 'major'
            else:
                if '7' in roman:
                    quality = 'minor7'
                elif '°' in roman or 'dim' in roman:
                    quality = 'diminished'
                else:
                    quality = 'minor'

            # Create chord
            chord = self._create_chord(root, quality, duration, octave, voicing_type)
            chords.append(chord)

        return Progression(chords, self.key, pattern)

    def generate_jazz_progression(
        self,
        num_chords: int = 8,
        complexity: float = 0.5,
        duration: float = 1.0,
        octave: int = 4
    ) -> Progression:
        """
        Generate jazz-style progression with extensions.

        Args:
            num_chords: Number of chords to generate
            complexity: Complexity level (0.0-1.0, affects extensions and substitutions)
            duration: Duration for each chord
            octave: Base octave

        Returns:
            Progression object
        """
        logger.info(f"Generating jazz progression with {num_chords} chords")

        # Common jazz progressions
        jazz_patterns = [
            ['Imaj7', 'vi7', 'ii7', 'V7'],  # I-vi-ii-V
            ['ii7', 'V7', 'Imaj7', 'Imaj7'],  # ii-V-I
            ['Imaj7', 'IV7', 'iii7', 'vi7'],  # Descending
            ['vi7', 'ii7', 'V7', 'Imaj7'],  # vi-ii-V-I
        ]

        pattern = []
        while len(pattern) < num_chords:
            jazz_pattern = random.choice(jazz_patterns)
            pattern.extend(jazz_pattern)

        pattern = pattern[:num_chords]

        # Add complexity (extensions, alterations)
        if complexity > 0.5:
            pattern = [self._add_jazz_extensions(rn) for rn in pattern]

        return self.generate_functional_progression(pattern, duration, 'close', octave)

    def generate_modal_progression(
        self,
        mode: str,
        num_chords: int = 4,
        duration: float = 1.0,
        octave: int = 4
    ) -> Progression:
        """
        Generate modal progression.

        Args:
            mode: Mode name (e.g., 'dorian', 'mixolydian')
            num_chords: Number of chords
            duration: Duration for each chord
            octave: Base octave

        Returns:
            Progression object
        """
        logger.info(f"Generating {mode} modal progression")

        # Create modal scale
        modal_scale = Scale(self.key.tonic, mode)

        # Generate chords from modal scale degrees
        chords = []
        degrees = [1, 4, 5, 1]  # Simple modal pattern

        for i in range(num_chords):
            degree = degrees[i % len(degrees)]
            root = modal_scale.get_degree(degree)

            # Build chord from modal scale
            chord_pitches = modal_scale.get_chord(degree, num_notes=3)
            notes = [Note(pc, duration, octave=octave) for pc in chord_pitches]
            chord = Chord(notes, duration, root)
            chords.append(chord)

        return Progression(chords, self.key)

    def _parse_roman_numeral(self, roman: str) -> int:
        """Parse Roman numeral to scale degree."""
        # Remove quality indicators
        clean = roman.replace('maj', '').replace('dim', '').replace('°', '')
        clean = clean.replace('7', '').replace('9', '').replace('11', '').replace('13', '')

        roman_map = {
            'I': 1, 'i': 1,
            'II': 2, 'ii': 2,
            'III': 3, 'iii': 3,
            'IV': 4, 'iv': 4,
            'V': 5, 'v': 5,
            'VI': 6, 'vi': 6,
            'VII': 7, 'vii': 7,
        }

        return roman_map.get(clean, 1)

    def _create_chord(
        self,
        root: 'PitchClass',
        quality: str,
        duration: float,
        octave: int,
        voicing_type: str
    ) -> Chord:
        """Create chord with specified voicing."""
        # Create basic chord
        symbol = f"{root.name}{quality.replace('major', '').replace('minor', 'm')}"
        chord = Chord.from_symbol(symbol, duration, octave)

        # Apply voicing
        if voicing_type == 'open':
            # Spread out the notes
            notes = chord.notes
            if len(notes) >= 3:
                notes[1] = notes[1].transpose(12)  # Raise middle note an octave
            chord = Chord(notes, duration, root)

        return chord

    def _add_jazz_extensions(self, roman: str) -> str:
        """Add jazz extensions to Roman numeral."""
        if '7' not in roman:
            if random.random() < 0.7:
                roman += '7'

        if random.random() < 0.3:
            if '9' not in roman:
                roman += '9'

        return roman


class VoicingGenerator:
    """Generate chord voicings."""

    def __init__(self):
        """Initialize voicing generator."""
        pass

    def generate_voicing(
        self,
        chord: Chord,
        voicing_type: str = 'close',
        range_constraint: tuple = (48, 72)
    ) -> Chord:
        """
        Generate specific voicing for a chord.

        Args:
            chord: Input chord
            voicing_type: Type of voicing ('close', 'open', 'drop2', 'drop3', 'spread')
            range_constraint: MIDI range (min, max)

        Returns:
            Re-voiced Chord
        """
        notes = list(chord.notes)

        if voicing_type == 'close':
            # Keep notes close together
            return chord

        elif voicing_type == 'open':
            # Spread notes across wider range
            if len(notes) >= 3:
                notes[1] = notes[1].transpose(12)
                if len(notes) >= 4:
                    notes[2] = notes[2].transpose(12)

        elif voicing_type == 'drop2':
            # Drop second-highest note down an octave
            if len(notes) >= 2:
                notes[-2] = notes[-2].transpose(-12)

        elif voicing_type == 'drop3':
            # Drop third-highest note down an octave
            if len(notes) >= 3:
                notes[-3] = notes[-3].transpose(-12)

        elif voicing_type == 'spread':
            # Spread notes evenly across range
            for i in range(1, len(notes)):
                notes[i] = notes[i].transpose(12 * (i // 2))

        # Ensure notes are within range
        notes = [self._clamp_note(n, range_constraint) for n in notes]

        return Chord(notes, chord.duration, chord.root)

    def _clamp_note(self, note: Note, range_constraint: tuple) -> Note:
        """Clamp note to range by octave transposition."""
        midi = note.get_midi_number()

        while midi < range_constraint[0]:
            midi += 12
        while midi > range_constraint[1]:
            midi -= 12

        return Note(midi, note.duration, note.velocity)

    def generate_voice_leading(
        self,
        progression: Progression,
        voice_leading_type: str = 'smooth'
    ) -> Progression:
        """
        Generate voice leading for progression.

        Args:
            progression: Input progression
            voice_leading_type: Type of voice leading ('smooth', 'contrary', 'parallel')

        Returns:
            Progression with optimized voice leading
        """
        logger.info(f"Generating {voice_leading_type} voice leading")

        if voice_leading_type == 'smooth':
            # Minimize voice leading distance
            new_chords = [progression.chords[0]]

            for i in range(1, len(progression.chords)):
                prev_chord = new_chords[-1]
                current_chord = progression.chords[i]

                # Find best voicing to minimize movement
                best_voicing = self._find_closest_voicing(prev_chord, current_chord)
                new_chords.append(best_voicing)

            return Progression(new_chords, progression.key)

        return progression

    def _find_closest_voicing(self, prev_chord: Chord, current_chord: Chord) -> Chord:
        """Find voicing that minimizes voice leading distance."""
        # Try different inversions
        best_chord = current_chord
        best_distance = float('inf')

        for inversion in range(len(current_chord.notes)):
            inverted = current_chord.invert(inversion)
            distance = self._voice_leading_distance(prev_chord, inverted)

            if distance < best_distance:
                best_distance = distance
                best_chord = inverted

        return best_chord

    def _voice_leading_distance(self, chord1: Chord, chord2: Chord) -> float:
        """Calculate total voice leading distance between two chords."""
        notes1 = sorted([n.get_midi_number() for n in chord1.notes])
        notes2 = sorted([n.get_midi_number() for n in chord2.notes])

        # Pad shorter chord
        max_len = max(len(notes1), len(notes2))
        notes1 += [notes1[-1]] * (max_len - len(notes1))
        notes2 += [notes2[-1]] * (max_len - len(notes2))

        # Calculate total distance
        return sum(abs(n1 - n2) for n1, n2 in zip(notes1, notes2))
