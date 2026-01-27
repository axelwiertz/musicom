"""Converters between music21 scales/keys and MusicPitchClassSet objects."""
from structures import PatternType, MusicPitchClassSet
from music21 import note, scale, key


# Pattern converters
def key_to_pattern(m21key: key.Key) -> MusicPitchClassSet:
    """Convert music21 key to MusicPitchClassSet."""

    # Assuming a standard heptatonic scale from a key
    pattern = MusicPitchClassSet(
                    name="Heptatonic Scale from Key",
                    definition=PatternType.HEPTATONIC,
                   )
    # Set mode and tonic
    pattern.set_rotation_name(m21key.mode)
    pattern.set_tonic(m21key.tonic.pitchClass)

    return pattern


def pattern_to_m21scale(pattern: MusicPitchClassSet) -> scale.ConcreteScale:
    # Convert pattern to music21 scale
    m21scale = scale.ConcreteScale()
    # Diatonic (7 pitch class) scale
    if pattern.type == PatternType.HEPTATONIC:
        # m21 scale from key
        m21key = key.Key(mode=pattern.rotation_name, tonic=note.Pitch(pattern.tonic_pitch_class))
        m21scale = m21key.getScale()

    return m21scale

