"""
Negative Harmony Mapping Transformer (Method 014)

Mirrors symbolic pitches across a central tonal axis to generate
tonal reflections and dark alterations.
"""

from structures.matrix import MusicUnit
from structures.unit import MusicEvent

class NegativeHarmonyTransformer:
    """
    Transforms the pitches of a MusicUnit using axis-based Negative Harmony mirroring.
    Axis is typically established between the Tonic fifth scale-degrees.
    e.g., in C Major, the axis is half-way between C (60) and G (67) -> 63.5.
    Formula: P_new = Axis_Low + Axis_High - P_old.
    """
    def __init__(self, key_center: int = 60):
        """
        Args:
            key_center: Midi note representing the tonal center (e.g., 60 = C).
        """
        self.key_center = key_center
        # Axis of reflection: between the tonic (0 semitones) and dominant (7 semitones)
        self.axis_low = key_center
        self.axis_high = key_center + 7

    def transform(self, unit: MusicUnit) -> MusicUnit:
        """
        Transforms the input MusicUnit and returns a new mirrored MusicUnit.
        """
        transformed_unit = MusicUnit()
        
        for event in unit.events:
            # Mirror pitch across the 1/5 axis (axis_low + axis_high)
            mirrored_pitch = (self.axis_low + self.axis_high) - event.pitch
            
            # Keep pitch octave-equivalent if it wanders wildly out of range
            octave_shift = (event.pitch // 12) * 12
            while mirrored_pitch < octave_shift:
                mirrored_pitch += 12
            while mirrored_pitch > octave_shift + 11:
                mirrored_pitch -= 12
                
            new_event = MusicEvent(
                pitch=int(mirrored_pitch),
                volume=event.volume,
                start_tick=event.start_tick,
                end_tick=event.end_tick
            )
            transformed_unit.add_event(new_event)
            
        return transformed_unit
