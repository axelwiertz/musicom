"""
Pitch transformation module.

This module provides transformations for pitch-based operations.
"""

from typing import Union
from musicom.ai.core.structures import Note, Chord, Phrase, Progression
from musicom.ai.core.tet_system import PitchClass
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('pitch_transformers')


class Transposer:
    """Transpose musical elements by semitones."""

    def __init__(self, semitones: int):
        """
        Initialize transposer.

        Args:
            semitones: Number of semitones to transpose (positive = up, negative = down)
        """
        self.semitones = semitones

    def transform(
        self,
        element: Union[Note, Chord, Phrase, Progression]
    ) -> Union[Note, Chord, Phrase, Progression]:
        """
        Apply transposition to musical element.

        Args:
            element: Musical element to transpose

        Returns:
            Transposed element
        """
        logger.info(f"Transposing by {self.semitones} semitones")
        return element.transpose(self.semitones)


class Inverter:
    """Invert melodies and harmonies."""

    def __init__(
        self,
        axis: Union[str, PitchClass, int] = 'tonic',
        inversion_type: str = 'melodic'
    ):
        """
        Initialize inverter.

        Args:
            axis: Inversion axis ('tonic', PitchClass, or MIDI number)
            inversion_type: Type of inversion ('melodic' or 'harmonic')
        """
        self.axis = axis
        self.inversion_type = inversion_type

    def transform(self, element: Union[Note, Phrase]) -> Union[Note, Phrase]:
        """
        Apply inversion to musical element.

        Args:
            element: Musical element to invert

        Returns:
            Inverted element
        """
        logger.info(f"Inverting around axis: {self.axis}")

        if isinstance(element, Note):
            return self._invert_note(element)
        elif isinstance(element, Phrase):
            return self._invert_phrase(element)
        else:
            raise TypeError(f"Cannot invert type: {type(element)}")

    def _invert_note(self, note: Note) -> Note:
        """Invert a single note."""
        # Determine axis MIDI number
        if isinstance(self.axis, str) and self.axis == 'tonic':
            axis_midi = 60  # Middle C as default
        elif isinstance(self.axis, PitchClass):
            axis_midi = self.axis.to_midi_number(4)
        elif isinstance(self.axis, int):
            axis_midi = self.axis
        else:
            axis_midi = 60

        # Calculate inverted pitch
        note_midi = note.get_midi_number()
        distance = note_midi - axis_midi
        inverted_midi = axis_midi - distance

        return Note(inverted_midi, note.duration, note.velocity)

    def _invert_phrase(self, phrase: Phrase) -> Phrase:
        """Invert a phrase."""
        inverted_elements = []

        for element in phrase.elements:
            if isinstance(element, Note):
                inverted_elements.append(self._invert_note(element))
            elif isinstance(element, Chord):
                # Invert each note in the chord
                inverted_notes = [self._invert_note(n) for n in element.notes]
                inverted_chord = Chord(inverted_notes, element.duration, element.root)
                inverted_elements.append(inverted_chord)
            else:
                # Keep rests as-is
                inverted_elements.append(element)

        return Phrase(
            inverted_elements,
            phrase.tempo,
            (phrase.time_signature.numerator, phrase.time_signature.denominator)
        )


class Retrograder:
    """Reverse musical sequences."""

    def __init__(self, reverse_rhythm: bool = True):
        """
        Initialize retrograder.

        Args:
            reverse_rhythm: Whether to reverse rhythm as well as pitch
        """
        self.reverse_rhythm = reverse_rhythm

    def transform(self, element: Union[Phrase, list]) -> Union[Phrase, list]:
        """
        Apply retrograde transformation.

        Args:
            element: Musical element to reverse

        Returns:
            Reversed element
        """
        logger.info("Applying retrograde transformation")

        if isinstance(element, Phrase):
            return self._retrograde_phrase(element)
        elif isinstance(element, list):
            return list(reversed(element))
        else:
            raise TypeError(f"Cannot retrograde type: {type(element)}")

    def _retrograde_phrase(self, phrase: Phrase) -> Phrase:
        """Retrograde a phrase."""
        reversed_elements = list(reversed(phrase.elements))

        if self.reverse_rhythm:
            # Keep reversed order with original timings
            return Phrase(
                reversed_elements,
                phrase.tempo,
                (phrase.time_signature.numerator, phrase.time_signature.denominator)
            )
        else:
            # Reverse pitches but keep original rhythm
            new_elements = []
            for i, element in enumerate(phrase.elements):
                reversed_element = reversed_elements[i]

                if isinstance(element, Note) and isinstance(reversed_element, Note):
                    # Use reversed pitch with original duration
                    new_note = Note(
                        reversed_element.get_midi_number(),
                        element.duration,
                        element.velocity
                    )
                    new_elements.append(new_note)
                else:
                    new_elements.append(element)

            return Phrase(
                new_elements,
                phrase.tempo,
                (phrase.time_signature.numerator, phrase.time_signature.denominator)
            )


class Augmenter:
    """Augment or diminish intervals."""

    def __init__(self, factor: float):
        """
        Initialize augmenter.

        Args:
            factor: Augmentation factor (>1 = augment, <1 = diminish)
        """
        self.factor = factor

    def transform(self, phrase: Phrase) -> Phrase:
        """
        Apply interval augmentation/diminution.

        Args:
            phrase: Phrase to transform

        Returns:
            Transformed phrase
        """
        logger.info(f"Augmenting intervals by factor: {self.factor}")

        if not phrase.elements:
            return phrase

        # Get first note as reference
        notes = [e for e in phrase.elements if isinstance(e, Note)]
        if not notes:
            return phrase

        reference_midi = notes[0].get_midi_number()
        new_elements = []

        for element in phrase.elements:
            if isinstance(element, Note):
                # Calculate interval from reference
                interval = element.get_midi_number() - reference_midi
                # Apply factor
                new_interval = int(interval * self.factor)
                new_midi = reference_midi + new_interval

                new_note = Note(new_midi, element.duration, element.velocity)
                new_elements.append(new_note)
            else:
                new_elements.append(element)

        return Phrase(
            new_elements,
            phrase.tempo,
            (phrase.time_signature.numerator, phrase.time_signature.denominator)
        )
