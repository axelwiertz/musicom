"""
Voice leading rules module.

This module provides rules for voice leading validation and optimization.
"""

from typing import List, Tuple, Dict, Any, Optional
from musicom.ai.core.structures import Chord, Progression
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('voice_leading_rules')


class VoiceLeadingRules:
    """Voice leading rules and validation."""

    def __init__(self, style: str = 'classical'):
        """
        Initialize voice leading rules.

        Args:
            style: Style of voice leading ('classical', 'jazz', 'pop')
        """
        self.style = style

        # Style-specific strictness
        self.allow_parallel_fifths = (style != 'classical')
        self.allow_parallel_octaves = (style != 'classical')
        self.allow_voice_crossing = (style in ['jazz', 'pop'])

    def check_parallel_motion(
        self,
        chord1: Chord,
        chord2: Chord
    ) -> List[str]:
        """
        Check for parallel fifths and octaves.

        Args:
            chord1: First chord
            chord2: Second chord

        Returns:
            List of violation messages
        """
        violations = []

        notes1 = sorted(chord1.notes, key=lambda n: n.get_midi_number())
        notes2 = sorted(chord2.notes, key=lambda n: n.get_midi_number())

        # Check all voice pairs
        for i in range(len(notes1)):
            for j in range(i + 1, len(notes1)):
                if i < len(notes2) and j < len(notes2):
                    # Calculate intervals
                    interval1 = notes1[j].get_midi_number() - notes1[i].get_midi_number()
                    interval2 = notes2[j].get_midi_number() - notes2[i].get_midi_number()

                    # Check for parallel fifths
                    if not self.allow_parallel_fifths:
                        if interval1 % 12 == 7 and interval2 % 12 == 7:
                            # Both are perfect fifths
                            motion1 = notes2[i].get_midi_number() - notes1[i].get_midi_number()
                            motion2 = notes2[j].get_midi_number() - notes1[j].get_midi_number()

                            if motion1 == motion2 and motion1 != 0:
                                violations.append(
                                    f"Parallel fifths between voices {i+1} and {j+1}"
                                )

                    # Check for parallel octaves
                    if not self.allow_parallel_octaves:
                        if interval1 % 12 == 0 and interval2 % 12 == 0:
                            motion1 = notes2[i].get_midi_number() - notes1[i].get_midi_number()
                            motion2 = notes2[j].get_midi_number() - notes1[j].get_midi_number()

                            if motion1 == motion2 and motion1 != 0:
                                violations.append(
                                    f"Parallel octaves between voices {i+1} and {j+1}"
                                )

        return violations

    def check_voice_crossing(self, chord: Chord) -> bool:
        """
        Check for voice crossing.

        Args:
            chord: Chord to check

        Returns:
            True if voice crossing detected
        """
        if self.allow_voice_crossing:
            return False

        notes = chord.notes
        for i in range(len(notes) - 1):
            if notes[i].get_midi_number() > notes[i + 1].get_midi_number():
                return True

        return False

    def optimize_voice_leading(
        self,
        progression: Progression
    ) -> Progression:
        """
        Optimize voice leading in progression.

        Args:
            progression: Progression to optimize

        Returns:
            Optimized Progression
        """
        logger.info("Optimizing voice leading")

        if len(progression.chords) < 2:
            return progression

        optimized_chords = [progression.chords[0]]

        for i in range(1, len(progression.chords)):
            prev_chord = optimized_chords[-1]
            current_chord = progression.chords[i]

            # Find best voicing
            best_chord = self._find_best_voicing(prev_chord, current_chord)
            optimized_chords.append(best_chord)

        return Progression(optimized_chords, progression.key)

    def _find_best_voicing(self, prev_chord: Chord, current_chord: Chord) -> Chord:
        """Find voicing that minimizes voice leading distance."""
        # Try different inversions
        best_chord = current_chord
        best_distance = self.calculate_voice_leading_distance(prev_chord, current_chord)

        for inversion in range(1, min(4, len(current_chord.notes))):
            inverted = current_chord.invert(inversion)
            distance = self.calculate_voice_leading_distance(prev_chord, inverted)

            if distance < best_distance:
                best_distance = distance
                best_chord = inverted

        return best_chord

    def calculate_voice_leading_distance(
        self,
        chord1: Chord,
        chord2: Chord
    ) -> float:
        """
        Calculate total voice leading distance.

        Args:
            chord1: First chord
            chord2: Second chord

        Returns:
            Total distance in semitones
        """
        notes1 = sorted([n.get_midi_number() for n in chord1.notes])
        notes2 = sorted([n.get_midi_number() for n in chord2.notes])

        # Pad to same length
        max_len = max(len(notes1), len(notes2))
        notes1 += [notes1[-1]] * (max_len - len(notes1))
        notes2 += [notes2[-1]] * (max_len - len(notes2))

        # Calculate total distance
        return sum(abs(n1 - n2) for n1, n2 in zip(notes1, notes2))

    def validate_voice_ranges(
        self,
        chord: Chord,
        ranges: Dict[str, Tuple[int, int]]
    ) -> List[str]:
        """
        Validate that voices are within specified ranges.

        Args:
            chord: Chord to validate
            ranges: Dictionary of voice ranges (e.g., {'soprano': (60, 81)})

        Returns:
            List of violation messages
        """
        violations = []

        voice_names = list(ranges.keys())
        for i, note in enumerate(chord.notes):
            if i < len(voice_names):
                voice_name = voice_names[i]
                min_pitch, max_pitch = ranges[voice_name]

                midi = note.get_midi_number()
                if midi < min_pitch or midi > max_pitch:
                    violations.append(
                        f"{voice_name} out of range: {midi} (expected {min_pitch}-{max_pitch})"
                    )

        return violations

    def check_hidden_fifths(
        self,
        chord1: Chord,
        chord2: Chord
    ) -> List[str]:
        """
        Check for hidden (direct) fifths and octaves.

        Args:
            chord1: First chord
            chord2: Second chord

        Returns:
            List of violation messages
        """
        if self.style != 'classical':
            return []

        violations = []

        notes1 = sorted(chord1.notes, key=lambda n: n.get_midi_number())
        notes2 = sorted(chord2.notes, key=lambda n: n.get_midi_number())

        # Check outer voices (soprano and bass)
        if len(notes1) >= 2 and len(notes2) >= 2:
            # Soprano
            soprano1 = notes1[-1].get_midi_number()
            soprano2 = notes2[-1].get_midi_number()

            # Bass
            bass1 = notes1[0].get_midi_number()
            bass2 = notes2[0].get_midi_number()

            # Check if both move in same direction
            soprano_motion = soprano2 - soprano1
            bass_motion = bass2 - bass1

            if soprano_motion * bass_motion > 0:  # Same direction
                # Check if they arrive at fifth or octave
                final_interval = (soprano2 - bass2) % 12

                if final_interval in [0, 7]:  # Octave or fifth
                    # Check if soprano moves by leap
                    if abs(soprano_motion) > 2:
                        violations.append(
                            f"Hidden {['octave', 'fifth'][final_interval == 7]} in outer voices"
                        )

        return violations
