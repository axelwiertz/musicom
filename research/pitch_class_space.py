from itertools import permutations, combinations
from base import PitchClass

class PitchClassSpace:
    def __init__(self, num_items=3):

        # Combinations: and permutations of a set
        self.combinations = list(combinations (PitchClass.NUMBERS, num_items))
        self.permutations = list(permutations (PitchClass.NUMBERS, num_items))
