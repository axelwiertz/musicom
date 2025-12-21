from structures import Cardinality, PatternType, MusicPattern
from music21 import note, scale, key, stream


# Pattern converters
def key_to_pattern(m21key: key.Key) -> MusicPattern:
    """Convert music21 key to MusicPattern."""

    # Assuming a standard heptatonic scale from a key
    pattern = MusicPattern("Heptatonic Scale from Key",
                           cardinality=Cardinality.HEPTA,
                           pattern_type=PatternType.SCALE,
                           )
    # Set mode and tonic
    pattern.set_mode_name(m21key.mode)
    pattern.set_tonic_pitch_class(m21key.tonic.pitchClass)

    return pattern

def score_to_pattern(score: stream.Score) -> MusicPattern:
    key_ = score.analyze('key')
    return key_to_pattern(key_)


def pattern_to_m21scale(pattern: MusicPattern) -> scale.ConcreteScale:
    # Convert pattern to music21 scale
    m21scale = scale.ConcreteScale()
    # Diatonic (7 pitch class) scale
    if pattern.cardinality == Cardinality.HEPTA and pattern.pattern_type == PatternType.SCALE:
        # m21 scale from key
        m21key = key.Key(mode=pattern.mode_name, tonic=note.Pitch(pattern.tonic_pitch_class))
        m21scale = m21key.getScale()

    return m21scale

