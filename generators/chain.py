"""
Musicom generators
Markov chain music generator
"""
from random import choice
from collections import defaultdict

from generators.generator import Generator
from harmony import Scale7ChordHarmony, Scale7PitchDegree
from structures import MusicUnit


class MarkovChain(Generator):
    # Markov chain of transitions
    def __init__(self, source_unit : MusicUnit, train):
        # build transition dict
        super().__init__(source_unit)
        self.train = train
        self.trans = defaultdict(list)
        for a, b in zip(train, train[1:]):
            self.trans[a[0]].append(b[0])

    def sample(self, start, length=16):
        # generate a sequence of given length from start state
        out = [start]
        cur = start
        for _ in range(length - 1):
            choices = self.trans.get(cur) or list(self.trans.keys())
            # random choice from possible transitions
            cur = choice(choices)
            out.append(cur)
        return out


def markov_chain ():

    chord_chain = MarkovChain(Scale7ChordHarmony.movement_rules)
    gen_chords = chord_chain.sample('1', length=16)
    print('Generated chords by Markov chain: ' + str(gen_chords))

    pitch_chain = MarkovChain(Scale7PitchDegree.movement_rules)
    gen_pitches = pitch_chain.sample('1', length=16)
    print('Generated pitches by Markov chain: ' + str(gen_pitches))


