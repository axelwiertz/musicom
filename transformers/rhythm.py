"""
Rhythm transformation module.

This module provides transformations for rhythmic operations.
"""

from typing import Union, List
from musicom.ai.core.structures import Note, Chord, Phrase, Rest
from musicom.ai.utils.helpers import quantize_duration
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('rhythm_transformers')


class RhythmicAugmentation:
    """Stretch or compress rhythmic durations."""

    def __init__(self, factor: float):
        """
        Initialize rhythmic augmentation.

        Args:
            factor: Augmentation factor (>1 = slower, <1 = faster)
        """
        self.factor = factor

    def transform(
        self,
        element: Union[Note, Chord, Phrase, List[Union[Note, Chord, Rest]]]
    ) -> Union[Note, Chord, Phrase, List[Union[Note, Chord, Rest]]]:
        """
        Apply rhythmic augmentation/diminution.

        Args:
            element: Musical element to transform

        Returns:
            Transformed element with modified durations
        """
        logger.info(f"Applying rhythmic augmentation with factor: {self.factor}")

        if isinstance(element, Note):
            return Note(
                element.get_midi_number(),
                element.duration * self.factor,
                element.velocity,
                articulation=element.articulation
            )

        elif isinstance(element, Chord):
            new_notes = [
                Note(n.get_midi_number(), n.duration * self.factor, n.velocity)
                for n in element.notes
            ]
            return Chord(new_notes, element.duration * self.factor, element.root)

        elif isinstance(element, Rest):
            return Rest(element.duration * self.factor)

        elif isinstance(element, Phrase):
            new_elements = []
            for e in element.elements:
                new_elements.append(self.transform(e))

            return Phrase(
                new_elements,
                element.tempo,
                (element.time_signature.numerator, element.time_signature.denominator)
            )

        elif isinstance(element, list):
            return [self.transform(e) for e in element]

        else:
            raise TypeError(f"Cannot transform type: {type(element)}")


class Quantizer:
    """Quantize rhythmic durations to grid."""

    def __init__(self, resolution: int = 16):
        """
        Initialize quantizer.

        Args:
            resolution: Quantization resolution (16 = sixteenth notes, 8 = eighth notes, etc.)
        """
        self.resolution = resolution

    def transform(
        self,
        element: Union[Note, Chord, Phrase, List[Union[Note, Chord, Rest]]]
    ) -> Union[Note, Chord, Phrase, List[Union[Note, Chord, Rest]]]:
        """
        Apply quantization to rhythmic durations.

        Args:
            element: Musical element to quantize

        Returns:
            Quantized element
        """
        logger.info(f"Quantizing to resolution: {self.resolution}")

        if isinstance(element, Note):
            quantized_duration = quantize_duration(element.duration, self.resolution)
            return Note(
                element.get_midi_number(),
                quantized_duration,
                element.velocity,
                articulation=element.articulation
            )

        elif isinstance(element, Chord):
            quantized_duration = quantize_duration(element.duration, self.resolution)
            new_notes = [
                Note(n.get_midi_number(), quantized_duration, n.velocity)
                for n in element.notes
            ]
            return Chord(new_notes, quantized_duration, element.root)

        elif isinstance(element, Rest):
            quantized_duration = quantize_duration(element.duration, self.resolution)
            return Rest(quantized_duration)

        elif isinstance(element, Phrase):
            new_elements = []
            for e in element.elements:
                new_elements.append(self.transform(e))

            return Phrase(
                new_elements,
                element.tempo,
                (element.time_signature.numerator, element.time_signature.denominator)
            )

        elif isinstance(element, list):
            return [self.transform(e) for e in element]

        else:
            raise TypeError(f"Cannot quantize type: {type(element)}")


class RhythmicDisplacement:
    """Shift rhythmic positions by offset."""

    def __init__(self, offset: float):
        """
        Initialize rhythmic displacement.

        Args:
            offset: Time offset in beats (can be negative)
        """
        self.offset = offset

    def transform(self, phrase: Phrase) -> Phrase:
        """
        Apply rhythmic displacement to phrase.

        Args:
            phrase: Phrase to displace

        Returns:
            Displaced phrase
        """
        logger.info(f"Displacing rhythm by {self.offset} beats")

        new_elements = []
        for element in phrase.elements:
            # Create new element with displaced start time
            if isinstance(element, Note):
                new_note = Note(
                    element.get_midi_number(),
                    element.duration,
                    element.velocity,
                    articulation=element.articulation,
                    start_time=element.start_time + self.offset
                )
                new_elements.append(new_note)

            elif isinstance(element, Chord):
                new_notes = []
                for note in element.notes:
                    new_note = Note(
                        note.get_midi_number(),
                        note.duration,
                        note.velocity,
                        start_time=note.start_time + self.offset
                    )
                    new_notes.append(new_note)
                new_chord = Chord(new_notes, element.duration, element.root)
                new_elements.append(new_chord)

            elif isinstance(element, Rest):
                new_rest = Rest(element.duration, element.start_time + self.offset)
                new_elements.append(new_rest)

        return Phrase(
            new_elements,
            phrase.tempo,
            (phrase.time_signature.numerator, phrase.time_signature.denominator)
        )


class SwingTransformer:
    """Apply swing feel to straight rhythms."""

    def __init__(self, swing_ratio: float = 0.67):
        """
        Initialize swing transformer.

        Args:
            swing_ratio: Swing ratio (0.5 = straight, 0.67 = standard swing, 0.75 = heavy swing)
        """
        self.swing_ratio = swing_ratio

    def transform(self, phrase: Phrase) -> Phrase:
        """
        Apply swing feel to phrase.

        Args:
            phrase: Phrase to swing

        Returns:
            Swung phrase
        """
        logger.info(f"Applying swing with ratio: {self.swing_ratio}")

        new_elements = []
        beat_duration = 4.0 / phrase.time_signature.denominator

        for element in phrase.elements:
            if isinstance(element, Note):
                # Determine if note is on or off beat
                beat_position = element.start_time % beat_duration
                is_off_beat = abs(beat_position - beat_duration / 2) < 0.01

                if is_off_beat:
                    # Delay off-beat notes
                    swing_offset = beat_duration * (self.swing_ratio - 0.5)
                    new_start = element.start_time + swing_offset

                    new_note = Note(
                        element.get_midi_number(),
                        element.duration,
                        element.velocity,
                        articulation=element.articulation,
                        start_time=new_start
                    )
                    new_elements.append(new_note)
                else:
                    new_elements.append(element)

            else:
                new_elements.append(element)

        return Phrase(
            new_elements,
            phrase.tempo,
            (phrase.time_signature.numerator, phrase.time_signature.denominator)
        )
