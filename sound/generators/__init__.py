"""Event Core Framework - Generative pattern engines.

Inspired by Karst's Event Cores system: hand-rolled generative algorithms
with probability-based variations, parameter locking, and auto-patching.

Core types:
- MarkovCore: Markov chain-based pattern generation
- StochasticCore: Tendency mask / weighted random generation
- LSystemCore: L-system string rewriting
- EuclideanCore: Euclidean rhythm generation
- WeightedRandomCore: Simple weighted random selection
"""

from .event_core import (
    EventCore,
    MarkovCore,
    StochasticCore,
    LSystemCore,
    EuclideanCore,
    WeightedRandomCore,
    PatternSequencer
)

__all__ = [
    'EventCore',
    'MarkovCore',
    'StochasticCore',
    'LSystemCore',
    'EuclideanCore',
    'WeightedRandomCore',
    'PatternSequencer'
]
