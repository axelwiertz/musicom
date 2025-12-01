"""
Musicom generators
Markov chain music generator
"""
import random
import numpy as np
from typing import Optional, List
from numpy.typing import NDArray

from collections import defaultdict

from generators import Generator
from structures import MusicUnit


class MarkovChainGenerator(Generator):
    # Markov chain of transitions
    def __init__(self, train, start, length=16):
        # build transition dict
        super().__init__()
        self.train = train
        self.trans = defaultdict(list)
        for a, b in zip(train, train[1:]):
            self.trans[a[0]].append(b[0])
        self.start = start
        self.length = length
        self.np_generator = np.random.Generator

    def generate(self) -> List[MusicUnit]:
        unit = MusicUnit()
        # generate a sequence of given length from start state
        out = [self.start]
        cur = self.start
        for _ in range(self.length - 1):
            choices = self.trans.get(cur) or list(self.trans.keys())
            # random choice from possible transitions
            cur = random.choice(choices)
            out.append(cur)
        return [unit]

    def generate_sequence(
            self,
            length: int = 16,
            states: Optional[NDArray[np.int_]] = None,
            distribution: Optional[NDArray[np.float32]] = None,
    ) -> List[int]:
        # set safe defaults inside the function (avoid mutable defaults)
        if states is None:
            states = np.array([0, 1, 2], dtype=int)
        if distribution is None:
            distribution = np.array([
                [0.7, 0.2, 0.1],
                [0.1, 0.6, 0.3],
                [0.3, 0.3, 0.4],
            ], dtype=float)

        n = len(states)
        path: List[int] = []
        current = 0
        rng = np.random.default_rng()

        for _ in range(length):
            path.append(int(states[current]))
            current = int(rng.choice(n, p=distribution[current]))

        print("Markov chain path:", path)
        return path


    def generate_unit_from_sequence(
            self,
            sequence: List[int],
            pitch_map: Optional[dict[int, int]] = None,
            duration: int = 1,
            onset_interval: int = 1,
            volume: int = 100,
    ) -> MusicUnit:
        if pitch_map is None:
            pitch_map = {0: 60, 1: 62, 2: 64}  # Default mapping

        unit = MusicUnit()
        for state in sequence:
            pitch = pitch_map.get(state, 60)  # Default to MIDI 60 if state not in map
            unit.append(
                pitch=pitch,
                duration=duration,
                onset_interval=onset_interval,
                volume=volume
            )
        return unit


