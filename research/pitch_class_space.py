from itertools import permutations, combinations
from base import MusicPitchClass

class MusicPitchClassSpace:
    def __init__(self, num_items=3):

        # Combinations: and permutations of a set
        self.combinations = list(combinations (MusicPitchClass.NUMBERS, num_items))
        self.permutations = list(permutations (MusicPitchClass.NUMBERS, num_items))
