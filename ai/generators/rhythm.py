"""
Rhythm generation module.

This module provides algorithms for generating rhythmic patterns.
"""

from typing import List, Tuple, Optional
import random
import math

from musicom.ai.utils.constants import DEFAULT_TIME_SIGNATURE
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('rhythm')


class RhythmicPatternGenerator:
    """Generate rhythmic patterns."""

    def __init__(
        self,
        time_signature: Tuple[int, int] = DEFAULT_TIME_SIGNATURE,
        subdivision: int = 4
    ):
        """
        Initialize rhythmic pattern generator.

        Args:
            time_signature: Time signature as (numerator, denominator)
            subdivision: Subdivision level (4 = sixteenth notes, 3 = triplets, etc.)
        """
        self.time_signature = time_signature
        self.subdivision = subdivision
        self.beats_per_measure = time_signature[0]
        self.beat_value = 4.0 / time_signature[1]

    def generate_pattern(
        self,
        num_bars: int = 1,
        density: float = 0.5,
        syncopation: float = 0.3
    ) -> List[float]:
        """
        Generate rhythmic pattern as list of durations.

        Args:
            num_bars: Number of measures
            density: Note density (0.0-1.0, higher = more notes)
            syncopation: Syncopation level (0.0-1.0, higher = more off-beat notes)

        Returns:
            List of durations in beats
        """
        logger.info(f"Generating rhythm pattern: {num_bars} bars, density={density}")

        total_duration = self.beats_per_measure * num_bars
        quantum = self.beat_value / self.subdivision

        # Generate grid of possible note onsets
        num_subdivisions = int(total_duration / quantum)
        grid = [False] * num_subdivisions

        # Place notes based on density
        num_notes = int(num_subdivisions * density)

        # Strong beats (downbeats)
        strong_beats = []
        for i in range(num_bars):
            strong_beats.append(int(i * self.beats_per_measure / quantum))

        # Place notes on strong beats first
        for beat in strong_beats:
            if beat < len(grid):
                grid[beat] = True

        # Place remaining notes
        remaining = num_notes - len(strong_beats)
        available_positions = [i for i in range(len(grid)) if not grid[i]]

        # Bias towards on-beat or off-beat based on syncopation
        if syncopation > 0.5:
            # Prefer off-beat positions
            off_beat_positions = [i for i in available_positions
                                if (i % (self.subdivision // 2)) != 0]
            if off_beat_positions:
                available_positions = off_beat_positions

        # Randomly place remaining notes
        if remaining > 0 and available_positions:
            selected = random.sample(available_positions, min(remaining, len(available_positions)))
            for pos in selected:
                grid[pos] = True

        # Convert grid to durations
        durations = []
        i = 0
        while i < len(grid):
            if grid[i]:
                # Find duration until next note or end
                duration = quantum
                j = i + 1
                while j < len(grid) and not grid[j]:
                    duration += quantum
                    j += 1
                durations.append(duration)
                i = j
            else:
                i += 1

        return durations

    def generate_euclidean_rhythm(
        self,
        pulses: int,
        steps: int
    ) -> List[float]:
        """
        Generate Euclidean rhythm pattern.

        Euclidean rhythms distribute pulses as evenly as possible across steps.

        Args:
            pulses: Number of pulses (notes)
            steps: Total number of steps

        Returns:
            List of durations
        """
        logger.info(f"Generating Euclidean rhythm: {pulses} pulses in {steps} steps")

        if pulses >= steps:
            # Every step is a pulse
            return [self.beat_value / self.subdivision] * steps

        # Bjorklund's algorithm
        pattern = self._bjorklund(pulses, steps)

        # Convert binary pattern to durations
        durations = []
        current_duration = 0
        quantum = self.beat_value / self.subdivision

        for i, is_pulse in enumerate(pattern):
            current_duration += quantum
            if is_pulse:
                if current_duration > 0:
                    durations.append(current_duration)
                    current_duration = 0

        # Add final duration if any
        if current_duration > 0:
            if durations:
                durations[-1] += current_duration

        return durations

    def _bjorklund(self, pulses: int, steps: int) -> List[bool]:
        """
        Bjorklund's algorithm for Euclidean rhythms.

        Args:
            pulses: Number of pulses
            steps: Total steps

        Returns:
            Binary pattern (True = pulse, False = rest)
        """
        if pulses == 0:
            return [False] * steps

        pattern = [[True]] * pulses + [[False]] * (steps - pulses)

        while len(set(map(tuple, pattern))) > 1:
            # Find the two most common groups
            groups = {}
            for p in pattern:
                key = tuple(p)
                groups[key] = groups.get(key, 0) + 1

            if len(groups) <= 1:
                break

            # Get two largest groups
            sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_groups) < 2:
                break

            group1, count1 = sorted_groups[0]
            group2, count2 = sorted_groups[1]

            # Combine groups
            new_pattern = []
            combined = min(count1, count2)

            for i in range(combined):
                new_pattern.append(list(group1) + list(group2))

            # Add remaining
            for i in range(count1 - combined):
                new_pattern.append(list(group1))
            for i in range(count2 - combined):
                new_pattern.append(list(group2))

            pattern = new_pattern

        # Flatten pattern
        result = []
        for group in pattern:
            result.extend(group)

        return result[:steps]

    def generate_swing_pattern(
        self,
        num_beats: int,
        swing_ratio: float = 0.67
    ) -> List[float]:
        """
        Generate swing rhythm pattern.

        Args:
            num_beats: Number of beats
            swing_ratio: Swing ratio (0.5 = straight, 0.67 = standard swing)

        Returns:
            List of durations with swing feel
        """
        logger.info(f"Generating swing pattern: {num_beats} beats, ratio={swing_ratio}")

        durations = []
        beat_duration = self.beat_value

        for i in range(num_beats * 2):  # Two eighth notes per beat
            if i % 2 == 0:
                # First eighth note (longer in swing)
                duration = beat_duration * swing_ratio
            else:
                # Second eighth note (shorter in swing)
                duration = beat_duration * (1 - swing_ratio)

            durations.append(duration)

        return durations

    def generate_polyrhythm(
        self,
        ratio: Tuple[int, int],
        duration: float
    ) -> Tuple[List[float], List[float]]:
        """
        Generate polyrhythmic pattern.

        Args:
            ratio: Polyrhythm ratio (e.g., (3, 2) for 3 against 2)
            duration: Total duration

        Returns:
            Tuple of two rhythm patterns
        """
        logger.info(f"Generating polyrhythm: {ratio[0]}:{ratio[1]}")

        rhythm1 = [duration / ratio[0]] * ratio[0]
        rhythm2 = [duration / ratio[1]] * ratio[1]

        return (rhythm1, rhythm2)

    def generate_clave_pattern(self, clave_type: str = 'son') -> List[float]:
        """
        Generate clave rhythm pattern.

        Args:
            clave_type: Type of clave ('son', 'rumba', 'bossa')

        Returns:
            List of durations
        """
        logger.info(f"Generating {clave_type} clave pattern")

        # Clave patterns (in sixteenth note subdivisions)
        patterns = {
            'son': [3, 3, 2, 2, 2, 4],  # 3-2 son clave
            'rumba': [3, 3, 2, 3, 1, 4],  # 3-2 rumba clave
            'bossa': [3, 2, 1, 2, 2, 2, 4],  # Bossa nova clave
        }

        if clave_type not in patterns:
            clave_type = 'son'

        # Convert to durations
        quantum = self.beat_value / 4  # Sixteenth note
        durations = [count * quantum for count in patterns[clave_type]]

        return durations

    def quantize_rhythm(
        self,
        durations: List[float],
        resolution: int = 16
    ) -> List[float]:
        """
        Quantize rhythm to nearest subdivision.

        Args:
            durations: Input durations
            resolution: Quantization resolution (16 = sixteenth notes)

        Returns:
            Quantized durations
        """
        quantum = self.beat_value / (resolution / 4)

        quantized = []
        for duration in durations:
            # Round to nearest quantum
            num_quanta = round(duration / quantum)
            quantized_duration = max(1, num_quanta) * quantum
            quantized.append(quantized_duration)

        return quantized
