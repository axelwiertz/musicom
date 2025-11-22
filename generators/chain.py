"""
Musicom generators
Markov chain music generator
"""
from typing import List
from random import choice
from collections import defaultdict


from generators import Generator
from regularity.progression import Scale7ChordHarmony, Scale7PitchDegree
from structures import MusicUnit


class MarkovChainGenerator(Generator):
    # Markov chain of transitions
    def __init__(self, seed_unit : MusicUnit, train, start, length=16):
        # build transition dict
        super().__init__(seed_unit)
        self.train = train
        self.trans = defaultdict(list)
        for a, b in zip(train, train[1:]):
            self.trans[a[0]].append(b[0])
        self.start = start
        self.length = length

    def generate(self) -> List[MusicUnit]:
        unit = MusicUnit()
        # generate a sequence of given length from start state
        out = [self.start]
        cur = self.start
        for _ in range(self.length - 1):
            choices = self.trans.get(cur) or list(self.trans.keys())
            # random choice from possible transitions
            cur = choice(choices)
            out.append(cur)
        return [unit]


def markov_chain ():

    unit1 = MusicUnit()
    gen = MarkovChainGenerator(unit1,train=Scale7ChordHarmony.movement_rules, start='1', length=16)
    unit = gen.generate()
    print('Generated chords by Markov chain: ' + unit)

    gen = MarkovChainGenerator(unit1, train=Scale7PitchDegree.movement_rules, start='1', length=16)
    unit = gen.generate()
    print('Generated pitches by Markov chain: ' + unit)


