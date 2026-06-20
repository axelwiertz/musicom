"""
Melody generation module.

This module provides various algorithms for generating melodies.
"""

from typing import List, Optional, Dict, Tuple
import random
import numpy as np

from musicom.ai.core.structures import Note, Phrase
from musicom.ai.core.tet_system import Scale, PitchClass
from musicom.ai.utils.constants import DEFAULT_TEMPO, DEFAULT_TIME_SIGNATURE
from musicom.ai.utils.validators import validate_midi_number
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('melody')


class RandomWalkGenerator:
    """Generate melodies using random walk algorithm."""

    def __init__(
        self,
        scale: Scale,
        step_weights: Optional[Dict[int, float]] = None,
        range_constraint: Tuple[int, int] = (48, 84)
    ):
        """
        Initialize random walk generator.

        Args:
            scale: Scale to use for melody
            step_weights: Weights for step sizes (default: favor small steps)
            range_constraint: MIDI range (min, max)
        """
        self.scale = scale
        self.range_constraint = range_constraint

        # Default weights favor stepwise motion
        if step_weights is None:
            self.step_weights = {
                -2: 0.1,  # Down 2 scale degrees
                -1: 0.3,  # Down 1 scale degree
                0: 0.2,   # Same note
                1: 0.3,   # Up 1 scale degree
                2: 0.1,   # Up 2 scale degrees
            }
        else:
            self.step_weights = step_weights

    def generate(
        self,
        length: int,
        start_pitch: Optional[PitchClass] = None,
        rhythm_pattern: Optional[List[float]] = None,
        tempo: float = DEFAULT_TEMPO
    ) -> Phrase:
        """
        Generate melody of specified length.

        Args:
            length: Number of notes to generate
            start_pitch: Starting pitch class (uses scale tonic if not specified)
            rhythm_pattern: List of durations (cycles if shorter than length)
            tempo: Tempo in BPM

        Returns:
            Generated Phrase
        """
        logger.info(f"Generating random walk melody with {length} notes")

        # Start pitch
        if start_pitch is None:
            start_pitch = self.scale.tonic

        # Default rhythm: quarter notes
        if rhythm_pattern is None:
            rhythm_pattern = [1.0] * length

        # Get scale pitches
        scale_pitches = self.scale.get_pitches()
        scale_semitones = [p.semitone for p in scale_pitches]

        # Find starting position in scale
        current_semitone = start_pitch.semitone
        current_octave = 4

        # Ensure start is in scale
        if current_semitone not in scale_semitones:
            current_semitone = scale_semitones[0]

        notes = []

        for i in range(length):
            # Create note
            midi_number = (current_octave + 1) * 12 + current_semitone

            # Clamp to range
            midi_number = max(self.range_constraint[0],
                            min(midi_number, self.range_constraint[1]))

            duration = rhythm_pattern[i % len(rhythm_pattern)]
            note = Note(midi_number, duration)
            notes.append(note)

            # Choose next step
            steps = list(self.step_weights.keys())
            weights = list(self.step_weights.values())
            step = random.choices(steps, weights=weights)[0]

            # Find current position in scale
            try:
                current_index = scale_semitones.index(current_semitone)
            except ValueError:
                current_index = 0

            # Apply step
            new_index = current_index + step
            octave_change = 0

            # Handle wrapping
            while new_index < 0:
                new_index += len(scale_semitones)
                octave_change -= 1
            while new_index >= len(scale_semitones):
                new_index -= len(scale_semitones)
                octave_change += 1

            current_semitone = scale_semitones[new_index]
            current_octave += octave_change

        return Phrase(notes, tempo=tempo)


class ScaleBasedGenerator:
    """Generate melodies constrained to a scale."""

    def __init__(self, scale: Scale):
        """
        Initialize scale-based generator.

        Args:
            scale: Scale to use for melody
        """
        self.scale = scale

    def generate(
        self,
        length: int,
        pattern: str = 'ascending',
        start_octave: int = 4,
        rhythm_pattern: Optional[List[float]] = None,
        tempo: float = DEFAULT_TEMPO
    ) -> Phrase:
        """
        Generate scale-based melody.

        Args:
            length: Number of notes to generate
            pattern: Pattern type ('ascending', 'descending', 'random', 'arpeggiate')
            start_octave: Starting octave
            rhythm_pattern: List of durations
            tempo: Tempo in BPM

        Returns:
            Generated Phrase
        """
        logger.info(f"Generating {pattern} scale-based melody with {length} notes")

        if rhythm_pattern is None:
            rhythm_pattern = [1.0] * length

        scale_pitches = self.scale.get_pitches()
        notes = []

        if pattern == 'ascending':
            for i in range(length):
                degree = (i % len(scale_pitches)) + 1
                octave = start_octave + (i // len(scale_pitches))
                pitch = self.scale.get_degree(degree)
                duration = rhythm_pattern[i % len(rhythm_pattern)]
                note = Note(pitch, duration, octave=octave)
                notes.append(note)

        elif pattern == 'descending':
            for i in range(length):
                degree = len(scale_pitches) - (i % len(scale_pitches))
                octave = start_octave - (i // len(scale_pitches))
                pitch = self.scale.get_degree(degree)
                duration = rhythm_pattern[i % len(rhythm_pattern)]
                note = Note(pitch, duration, octave=octave)
                notes.append(note)

        elif pattern == 'random':
            for i in range(length):
                degree = random.randint(1, len(scale_pitches))
                octave = start_octave + random.randint(-1, 1)
                pitch = self.scale.get_degree(degree)
                duration = rhythm_pattern[i % len(rhythm_pattern)]
                note = Note(pitch, duration, octave=octave)
                notes.append(note)

        elif pattern == 'arpeggiate':
            # Use chord tones (1, 3, 5, 7)
            chord_degrees = [1, 3, 5]
            if len(scale_pitches) >= 7:
                chord_degrees.append(7)

            for i in range(length):
                degree = chord_degrees[i % len(chord_degrees)]
                octave = start_octave + (i // len(chord_degrees))
                pitch = self.scale.get_degree(degree)
                duration = rhythm_pattern[i % len(rhythm_pattern)]
                note = Note(pitch, duration, octave=octave)
                notes.append(note)

        return Phrase(notes, tempo=tempo)

    def generate_sequence(
        self,
        degrees: List[int],
        octave: int = 4,
        duration: float = 1.0,
        tempo: float = DEFAULT_TEMPO
    ) -> Phrase:
        """
        Generate melody from scale degree sequence.

        Args:
            degrees: List of scale degrees (1-indexed)
            octave: Octave number
            duration: Duration for each note
            tempo: Tempo in BPM

        Returns:
            Generated Phrase
        """
        notes = []
        for degree in degrees:
            pitch = self.scale.get_degree(degree)
            note = Note(pitch, duration, octave=octave)
            notes.append(note)

        return Phrase(notes, tempo=tempo)


class MarkovChainGenerator:
    """Generate melodies using Markov chains."""

    def __init__(self, order: int = 1):
        """
        Initialize Markov chain generator.

        Args:
            order: Order of Markov chain (1 = first-order, 2 = second-order, etc.)
        """
        self.order = order
        self.transitions: Dict[tuple, Dict[int, int]] = {}
        self.trained = False

    def train(self, training_phrases: List[Phrase]):
        """
        Train on existing melodies.

        Args:
            training_phrases: List of Phrase objects to learn from
        """
        logger.info(f"Training Markov chain on {len(training_phrases)} phrases")

        for phrase in training_phrases:
            notes = phrase.get_notes()
            midi_sequence = [n.get_midi_number() for n in notes]

            # Build transition table
            for i in range(len(midi_sequence) - self.order):
                # State is the previous 'order' notes
                state = tuple(midi_sequence[i:i + self.order])
                next_note = midi_sequence[i + self.order]

                if state not in self.transitions:
                    self.transitions[state] = {}

                if next_note not in self.transitions[state]:
                    self.transitions[state][next_note] = 0

                self.transitions[state][next_note] += 1

        self.trained = True
        logger.info(f"Training complete. Learned {len(self.transitions)} states")

    def generate(
        self,
        length: int,
        seed: Optional[List[Note]] = None,
        rhythm_pattern: Optional[List[float]] = None,
        tempo: float = DEFAULT_TEMPO
    ) -> Phrase:
        """
        Generate melody using trained model.

        Args:
            length: Number of notes to generate
            seed: Optional seed notes (must be at least 'order' notes)
            rhythm_pattern: List of durations
            tempo: Tempo in BPM

        Returns:
            Generated Phrase

        Raises:
            ValueError: If not trained or seed is invalid
        """
        if not self.trained:
            raise ValueError("Generator must be trained before generating")

        if rhythm_pattern is None:
            rhythm_pattern = [1.0] * length

        # Initialize with seed or random state
        if seed and len(seed) >= self.order:
            current_state = tuple(n.get_midi_number() for n in seed[:self.order])
            notes = list(seed[:self.order])
        else:
            # Random starting state
            current_state = random.choice(list(self.transitions.keys()))
            notes = [Note(midi, 1.0) for midi in current_state]

        # Generate remaining notes
        for i in range(len(notes), length):
            if current_state in self.transitions:
                # Choose next note based on probabilities
                next_notes = list(self.transitions[current_state].keys())
                weights = list(self.transitions[current_state].values())
                next_midi = random.choices(next_notes, weights=weights)[0]
            else:
                # Fallback to random state if current state not found
                current_state = random.choice(list(self.transitions.keys()))
                next_midi = current_state[0]

            duration = rhythm_pattern[i % len(rhythm_pattern)]
            note = Note(next_midi, duration)
            notes.append(note)

            # Update state
            current_state = tuple(n.get_midi_number() for n in notes[-self.order:])

        return Phrase(notes, tempo=tempo)
