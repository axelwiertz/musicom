"""Defines common rhythmic onset interval patterns."""

class OnsetIntervalPattern:
    """Common rhythmic onset interval patterns represented as tuples of integers."""
    _dict = {
        'Simple': (1,),
        'Two': (1, 1),
        'Three': (1, 1, 1),
        'Four': (1, 1, 1, 1),
        'Tresillo': (3, 3, 2),
        'Twelve Eighth Bell': (2, 2, 1, 2, 2, 2, 1),
        'Son Clave': (3, 3, 4, 2, 4)
    }
    @classmethod
    def get_pattern(cls, name: str):
        """Get onset interval pattern by name."""
        return cls._dict.get(name, (1,))  # Default to 'Simple' if name not found
    @classmethod
    def patterns(cls):
        """Get a list of available pattern names."""
        return list(cls._dict.keys())

class TempoRange:
    """Common tempo ranges in BPM for different music styles."""
    _dict = {
        'Ballad': (60, 80),
        'Pop': (100, 130),
        'Rock': (120, 160),
        'EDM / Dance': (120, 140),
        'Techno': (125, 150),
        'Drum & Bass': (160, 180),
        'Classical (Allegro)': (120, 168),
        'Classical (Adagio)': (66, 76)
    }
    @classmethod
    def get_range(cls, style: str):
        """Get tempo range for a given music style."""
        return cls._dict.get(style, (60, 120))  # Default to (60, 120) if style not found

    @classmethod
    def styles(cls):
        """Get a list of available music styles."""
        return list(cls._dict.keys())

