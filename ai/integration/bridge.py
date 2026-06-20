"""
Library bridge module.

This module provides a unified interface for all external music libraries.
"""

from typing import Any, Dict, Union, Optional
import numpy as np

from musicom.ai.core.structures import Note, Chord, Phrase
from musicom.ai.integration.converters import (
    Music21Converter,
    MusicPyConverter,
    PyPianorollConverter,
)
from musicom.ai.utils.exceptions import ConversionError
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('bridge')


class LibraryBridge:
    """Unified interface for all music libraries."""

    def __init__(self):
        """Initialize library bridge."""
        self.music21_converter = Music21Converter()
        self.musicpy_converter = MusicPyConverter()
        self.pianoroll_converter = PyPianorollConverter()

    def create_note(self, **kwargs) -> Note:
        """
        Create note using any library's parameters.

        Args:
            **kwargs: Note parameters (flexible format)

        Returns:
            Note object
        """
        # Support multiple parameter formats
        if 'pitch' in kwargs:
            return Note(**kwargs)
        elif 'midi' in kwargs:
            return Note(pitch=kwargs['midi'], duration=kwargs.get('duration', 1.0))
        elif 'name' in kwargs:
            return Note(pitch=kwargs['name'], duration=kwargs.get('duration', 1.0))
        else:
            raise ValueError("Must provide pitch, midi, or name parameter")

    def analyze_harmony(
        self,
        element: Any,
        library: str = 'music21'
    ) -> Dict[str, Any]:
        """
        Analyze harmony using specified library.

        Args:
            element: Musical element to analyze
            library: Library to use ('music21', 'musicpy')

        Returns:
            Dictionary of analysis results
        """
        logger.info(f"Analyzing harmony using {library}")

        if library == 'music21':
            try:
                import music21

                # Convert to Music21 if needed
                if isinstance(element, Chord):
                    m21_chord = self.music21_converter.chord_to_music21(element)
                    return {
                        'root': str(m21_chord.root()),
                        'quality': str(m21_chord.quality),
                        'inversion': m21_chord.inversion(),
                    }
                elif isinstance(element, Phrase):
                    # Analyze key
                    part = music21.stream.Part()
                    for e in element.elements:
                        if isinstance(e, Note):
                            part.append(self.music21_converter.note_to_music21(e))

                    key = part.analyze('key')
                    return {
                        'key': f"{key.tonic.name} {key.mode}",
                        'tonic': str(key.tonic.name),
                        'mode': key.mode,
                    }

            except Exception as e:
                raise ConversionError(f"Harmony analysis failed: {str(e)}")

        return {}

    def visualize(
        self,
        element: Any,
        method: str = 'pianoroll'
    ) -> Any:
        """
        Visualize using appropriate library.

        Args:
            element: Musical element to visualize
            method: Visualization method ('pianoroll', 'notation')

        Returns:
            Visualization object or None
        """
        logger.info(f"Visualizing using method: {method}")

        if method == 'pianoroll':
            try:
                import matplotlib.pyplot as plt

                if isinstance(element, Phrase):
                    pianoroll = self.pianoroll_converter.phrase_to_pianoroll(element)

                    plt.figure(figsize=(12, 6))
                    plt.imshow(pianoroll, aspect='auto', origin='lower', cmap='Blues')
                    plt.xlabel('Time (ticks)')
                    plt.ylabel('MIDI Pitch')
                    plt.title('Piano Roll Visualization')
                    plt.colorbar(label='Velocity')
                    return plt

            except ImportError:
                logger.warning("matplotlib not available for visualization")
                return None

        elif method == 'notation':
            try:
                import music21

                if isinstance(element, Phrase):
                    part = music21.stream.Part()
                    for e in element.elements:
                        if isinstance(e, Note):
                            part.append(self.music21_converter.note_to_music21(e))

                    part.show()
                    return part

            except ImportError:
                logger.warning("music21 not available for notation")
                return None

        return None

    def convert(
        self,
        element: Any,
        target_library: str
    ) -> Any:
        """
        Convert element to target library format.

        Args:
            element: Element to convert
            target_library: Target library ('music21', 'musicpy', 'pianoroll')

        Returns:
            Converted element

        Raises:
            ConversionError: If conversion fails
        """
        logger.info(f"Converting to {target_library}")

        try:
            if target_library == 'music21':
                if isinstance(element, Note):
                    return self.music21_converter.note_to_music21(element)
                elif isinstance(element, Chord):
                    return self.music21_converter.chord_to_music21(element)

            elif target_library == 'musicpy':
                if isinstance(element, Note):
                    return self.musicpy_converter.note_to_musicpy(element)
                elif isinstance(element, Chord):
                    return self.musicpy_converter.chord_to_musicpy(element)

            elif target_library == 'pianoroll':
                if isinstance(element, Phrase):
                    return self.pianoroll_converter.phrase_to_pianoroll(element)
                elif isinstance(element, list):
                    return self.pianoroll_converter.notes_to_pianoroll(element)

            raise ConversionError(f"Unsupported conversion: {type(element)} to {target_library}")

        except Exception as e:
            raise ConversionError(f"Conversion failed: {str(e)}") from e
