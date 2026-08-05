"""Rhythm transformation module.

Transformations for rhythmic operations on ``MusicUnit`` using the canonical
absolute-tick time model (``MusicEvent(pitch, volume, start_tick, end_tick)``).
"""

from structures.unit import MusicUnit, MusicEvent
from utilities.logging_config import get_logger
from .base import MusicTransformer

logger = get_logger('rhythm_transformers')


def _clone_with_events(unit: MusicUnit, transform_fn) -> MusicUnit:
    """Build a new MusicUnit by applying ``transform_fn`` to each event."""
    new_unit = MusicUnit()
    for e in unit.events:
        ne = transform_fn(e)
        if ne is not None:
            new_unit.add_event(ne)
    return new_unit


class RhythmicAugmentation(MusicTransformer):
    """Stretch or compress rhythmic durations (and their positions)."""

    def __init__(self, factor: float):
        """
        Initialize rhythmic augmentation.

        Args:
            factor: Augmentation factor (>1 = slower, <1 = faster)
        """
        super().__init__(None)
        self.factor = factor

    def transform(self, unit: MusicUnit = None) -> MusicUnit:
        """
        Apply rhythmic augmentation/diminution.

        Args:
            unit: MusicUnit to transform (falls back to the bound unit)

        Returns:
            Transformed MusicUnit with scaled ticks
        """
        unit = unit or self._unit
        logger.info(f"Applying rhythmic augmentation with factor: {self.factor}")

        def scale(e: MusicEvent) -> MusicEvent:
            return MusicEvent(
                pitch=e.pitch,
                volume=e.volume,
                start_tick=int(e.start_tick * self.factor),
                end_tick=int(e.end_tick * self.factor),
            )

        return _clone_with_events(unit, scale)


class Quantizer(MusicTransformer):
    """Quantize event ticks to a fixed grid resolution."""

    def __init__(self, resolution_ticks: int = 120):
        """
        Initialize quantizer.

        Args:
            resolution_ticks: Quantization grid in ticks (e.g. 120 = sixteenth
                at 480 ticks/beat, 240 = eighth, 480 = quarter)
        """
        super().__init__(None)
        if resolution_ticks <= 0:
            raise ValueError("resolution_ticks must be positive")
        self.resolution_ticks = resolution_ticks

    def transform(self, unit: MusicUnit = None) -> MusicUnit:
        """
        Apply quantization to event ticks.

        Args:
            unit: MusicUnit to quantize (falls back to the bound unit)

        Returns:
            Quantized MusicUnit
        """
        unit = unit or self._unit
        logger.info(f"Quantizing to resolution: {self.resolution_ticks} ticks")
        grid = self.resolution_ticks

        def quantize(e: MusicEvent) -> MusicEvent:
            start = round(e.start_tick / grid) * grid
            end = round(e.end_tick / grid) * grid
            if end <= start:
                end = start + grid
            return MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=start, end_tick=end)

        return _clone_with_events(unit, quantize)


class RhythmicDisplacement(MusicTransformer):
    """Shift event positions by a tick offset."""

    def __init__(self, offset_ticks: int):
        """
        Initialize rhythmic displacement.

        Args:
            offset_ticks: Offset in ticks (may be negative)
        """
        super().__init__(None)
        self.offset_ticks = offset_ticks

    def transform(self, unit: MusicUnit = None) -> MusicUnit:
        """
        Apply rhythmic displacement.

        Args:
            unit: MusicUnit to displace (falls back to the bound unit)

        Returns:
            Displaced MusicUnit
        """
        unit = unit or self._unit
        logger.info(f"Displacing rhythm by {self.offset_ticks} ticks")

        def displace(e: MusicEvent) -> MusicEvent:
            return MusicEvent(
                pitch=e.pitch,
                volume=e.volume,
                start_tick=max(0, e.start_tick + self.offset_ticks),
                end_tick=max(0, e.end_tick + self.offset_ticks),
            )

        return _clone_with_events(unit, displace)


class SwingTransformer(MusicTransformer):
    """Apply swing feel to straight rhythms by delaying off-beat events."""

    def __init__(self, swing_ratio: float = 0.67, ticks_per_beat: int = 480):
        """
        Initialize swing transformer.

        Args:
            swing_ratio: Swing ratio (0.5 = straight, 0.67 = standard swing,
                0.75 = heavy swing)
            ticks_per_beat: Resolution used to locate off-beats
        """
        super().__init__(None)
        self.swing_ratio = swing_ratio
        self.ticks_per_beat = ticks_per_beat

    def transform(self, unit: MusicUnit = None) -> MusicUnit:
        """
        Apply swing feel by delaying off-beat events.

        Args:
            unit: MusicUnit to swing (falls back to the bound unit)

        Returns:
            Swung MusicUnit
        """
        unit = unit or self._unit
        logger.info(f"Applying swing with ratio: {self.swing_ratio}")

        half_beat = self.ticks_per_beat / 2.0
        swing_offset = int(self.ticks_per_beat * (self.swing_ratio - 0.5))

        def swing(e: MusicEvent) -> MusicEvent:
            beat_position = e.start_tick % self.ticks_per_beat
            is_off_beat = abs(beat_position - half_beat) < 1e-6
            start = e.start_tick + swing_offset if is_off_beat else e.start_tick
            duration = e.end_tick - e.start_tick
            return MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=start, end_tick=start + duration)

        return _clone_with_events(unit, swing)
