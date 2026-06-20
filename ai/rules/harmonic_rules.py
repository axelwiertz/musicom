"""
Harmonic rules module.

This module provides music theory rules for harmonic analysis and validation.
"""

from typing import List, Tuple, Optional, Dict
from musicom.ai.core.structures import Chord, Progression
from musicom.ai.core.tet_system import Key
from musicom.ai.utils.constants import HARMONIC_FUNCTIONS
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('harmonic_rules')


class FunctionalHarmony:
    """Functional harmony rules and analysis."""

    FUNCTIONS = {
        'I': 'tonic', 'i': 'tonic',
        'II': 'subdominant', 'ii': 'subdominant',
        'III': 'tonic', 'iii': 'tonic',
        'IV': 'subdominant', 'iv': 'subdominant',
        'V': 'dominant', 'v': 'dominant',
        'VI': 'tonic', 'vi': 'tonic',
        'VII': 'dominant', 'vii': 'dominant',
        'vii°': 'dominant',
    }

    # Common progression patterns
    COMMON_PROGRESSIONS = {
        'authentic_cadence': ['V', 'I'],
        'plagal_cadence': ['IV', 'I'],
        'deceptive_cadence': ['V', 'vi'],
        'half_cadence': ['I', 'V'],
        'circle_of_fifths': ['I', 'IV', 'vii°', 'iii', 'vi', 'ii', 'V', 'I'],
        'jazz_turnaround': ['I', 'vi', 'ii', 'V'],
        'pop_progression': ['I', 'V', 'vi', 'IV'],
        'blues_progression': ['I', 'I', 'I', 'I', 'IV', 'IV', 'I', 'I', 'V', 'IV', 'I', 'V'],
    }

    def __init__(self, key: Key, strict: bool = False):
        """
        Initialize functional harmony analyzer.

        Args:
            key: Key context
            strict: Whether to apply strict classical rules
        """
        self.key = key
        self.strict = strict

    def validate_progression(
        self,
        progression: Progression
    ) -> Tuple[bool, List[str]]:
        """
        Validate progression and return violations.

        Args:
            progression: Progression to validate

        Returns:
            Tuple of (is_valid, list of violation messages)
        """
        logger.info(f"Validating progression in {self.key}")

        violations = []
        roman_numerals = progression.analyze()

        # Check for valid chord functions
        for i, roman in enumerate(roman_numerals):
            if roman not in self.FUNCTIONS and roman != '?':
                violations.append(f"Chord {i+1}: Unknown Roman numeral '{roman}'")

        # Check for proper cadences
        if len(roman_numerals) >= 2:
            last_two = roman_numerals[-2:]

            # Check if ends on tonic
            if self.strict and last_two[-1] not in ['I', 'i']:
                violations.append("Progression should end on tonic (I)")

        # Check for parallel motion (would need chord voicings)
        # This is a simplified check
        if self.strict:
            for i in range(len(roman_numerals) - 1):
                current = roman_numerals[i]
                next_chord = roman_numerals[i + 1]

                # Avoid V-IV (retrograde dominant motion)
                if current == 'V' and next_chord == 'IV':
                    violations.append(f"Chords {i+1}-{i+2}: Avoid V-IV progression")

        is_valid = len(violations) == 0
        return (is_valid, violations)

    def suggest_next_chord(
        self,
        current_chord: str,
        function_preference: Optional[str] = None
    ) -> List[str]:
        """
        Suggest possible next chords based on functional harmony.

        Args:
            current_chord: Current Roman numeral
            function_preference: Preferred function ('tonic', 'dominant', 'subdominant')

        Returns:
            List of suggested Roman numerals
        """
        logger.info(f"Suggesting next chord after {current_chord}")

        # Common progressions from each chord
        suggestions_map = {
            'I': ['ii', 'iii', 'IV', 'V', 'vi'],
            'ii': ['V', 'vii°'],
            'iii': ['vi', 'IV'],
            'IV': ['I', 'V', 'ii'],
            'V': ['I', 'vi'],  # Including deceptive cadence
            'vi': ['ii', 'IV', 'V'],
            'vii°': ['I'],
        }

        suggestions = suggestions_map.get(current_chord, ['I', 'IV', 'V'])

        # Filter by function preference
        if function_preference:
            filtered = [s for s in suggestions
                       if self.FUNCTIONS.get(s) == function_preference]
            if filtered:
                suggestions = filtered

        return suggestions

    def analyze_function(self, roman_numeral: str) -> str:
        """
        Get harmonic function of Roman numeral.

        Args:
            roman_numeral: Roman numeral to analyze

        Returns:
            Harmonic function ('tonic', 'dominant', 'subdominant')
        """
        return self.FUNCTIONS.get(roman_numeral, 'unknown')

    def identify_cadence(self, progression: Progression) -> Optional[str]:
        """
        Identify cadence type at end of progression.

        Args:
            progression: Progression to analyze

        Returns:
            Cadence type or None
        """
        roman_numerals = progression.analyze()

        if len(roman_numerals) < 2:
            return None

        last_two = roman_numerals[-2:]

        # Check for common cadences
        if last_two == ['V', 'I']:
            return 'authentic_cadence'
        elif last_two == ['IV', 'I']:
            return 'plagal_cadence'
        elif last_two == ['V', 'vi']:
            return 'deceptive_cadence'
        elif last_two[-1] == 'V':
            return 'half_cadence'

        return None

    def get_common_progression(self, name: str) -> List[str]:
        """
        Get a common progression pattern by name.

        Args:
            name: Progression name

        Returns:
            List of Roman numerals
        """
        return self.COMMON_PROGRESSIONS.get(name, ['I', 'IV', 'V', 'I'])
