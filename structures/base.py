"""Module defining the base class for musical structures."""

class MusicBase:
    # Base class for musical structures
    def __init__(self, _id: int = 0, name: str = 'MusicBase'):
        self._id = _id
        self.name = name

    def __repr__(self):
        return f"Instance(class='{self.__class__}', id={self._id}, name='{self.name}')"
