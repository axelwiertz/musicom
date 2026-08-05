"""Module for generating random music21 streams."""
import random
import numpy as np
from typing import List
from structures import MusicUnit
from structures.unit import MusicEvent
from .base import MusicGenerator

class StochasticGenerator(MusicGenerator):
    """Class for generating stochastic music21 streams."""

    def __init__(self,
                 length: int,
                 pitch_set: List[int],
                 duration_set: List[int]
                 ):
        super().__init__()
        self.length = length
        self.pitch_set = pitch_set
        self.duration_set = duration_set

    def generate(self) -> List[MusicUnit]:
        unit = MusicUnit()
        tick = 0
        for i in range(self.length):
            duration = random.choice(self.duration_set)
            unit.add_event(MusicEvent(
                pitch=random.choice(self.pitch_set),
                volume=random.randint(60, 100),
                start_tick=tick,
                end_tick=tick + duration,
            ))
            tick += duration
        return [unit]


def random_number_sampling():
    # Uniform in [0, 1)
    u01 = random.random()

    # Uniform in [a, b]
    a, b = -5, 5
    u_ab = random.uniform(a, b)

    # Random integer in [low, high] inclusive
    low, high = 1, 6
    roll = random.randint(low, high)

    print(u01, u_ab, roll)


def controlled_probability_sampling():
    # Set a seed for reproducibility (PRNG)
    np.random.seed(42)

    # Uniform: n samples in [0, 1)
    uniform_samples = np.random.uniform(0, 1, size=5)

    # Normal: mean mu, std sigma
    mu, sigma = 0.0, 1.0
    normal_samples = np.random.normal(mu, sigma, size=5)

    # Exponential: rate lambda => scale = 1/lambda
    lam = 2.0
    exponential_samples = np.random.exponential(scale=1 / lam, size=5)

    # Discrete weighted choice: values with probabilities p (sum to 1)
    values = np.array(['A', 'B', 'C'])
    p = np.array([0.2, 0.5, 0.3])
    discrete_choices = np.random.choice(values, size=10, p=p)

    print("Uniform:", uniform_samples)
    print("Normal:", normal_samples)
    print("Exponential:", exponential_samples)
    print("Weighted discrete:", discrete_choices)

