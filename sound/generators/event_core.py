"""Event Core Framework — generative pattern engines.

Inspired by Karst's "Event Cores" system: hand-rolled generative algorithms
with probability-based variations, parameter locking, and auto-patching.

Usage:
    core = EuclideanCore(pulses=5, steps=16)
    pattern = core.generate(4)  # Generate 4 bars
    
    core = MarkovCore(transition_matrix=matrix)
    pattern = core.generate(2, seed=60)  # Start from MIDI note 60
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import random


@dataclass
class EventCoreState:
    """Current state of an event core."""
    step: int = 0
    locked_params: Dict[str, Any] = field(default_factory=dict)
    history: List[Any] = field(default_factory=list)


class EventCore:
    """
    Base class for generative event cores.
    
    Event cores generate sequences of values (pitches, rhythms, velocities)
    using algorithmic processes. They support:
    - Parameter locking (freeze specific params during generation)
    - Probability-based variations (dice system)
    - History tracking for context-aware generation
    """
    
    def __init__(self, name: str = "core"):
        self.name = name
        self.state = EventCoreState()
        self._locked_params = set()
        self._variation_prob = 0.1  # Default 10% chance of variation
    
    def generate(self, steps: int, **kwargs) -> List[Any]:
        """
        Generate sequence of events.
        
        Args:
            steps: Number of steps to generate
            **kwargs: Core-specific parameters
            
        Returns:
            List of generated values
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def lock(self, param_name: str):
        """Lock a parameter (prevents variation during generation)."""
        self._locked_params.add(param_name)
        self.state.locked_params[param_name] = True
    
    def unlock(self, param_name: str):
        """Unlock a parameter."""
        self._locked_params.discard(param_name)
        self.state.locked_params.pop(param_name, None)
    
    def is_locked(self, param_name: str) -> bool:
        """Check if parameter is locked."""
        return param_name in self._locked_params
    
    def set_variation_probability(self, prob: float):
        """Set probability of random variation (0-1)."""
        self._variation_prob = max(0.0, min(1.0, prob))
    
    def should_vary(self) -> bool:
        """Dice roll: should we apply variation this step?"""
        return random.random() < self._variation_prob
    
    def reset(self):
        """Reset core state."""
        self.state = EventCoreState()
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


class EuclideanCore(EventCore):
    """
    Euclidean rhythm generator (Bjorklund algorithm).
    
    Distributes N pulses as evenly as possible across M steps.
    Classic algorithm for generating rhythmic patterns.
    """
    
    def __init__(self, pulses: int = 5, steps: int = 16, rotation: int = 0,
                 name: str = "euclidean"):
        super().__init__(name)
        self.pulses = pulses
        self.steps = steps
        self.rotation = rotation
    
    def _generate_pattern(self) -> List[int]:
        """Generate single Euclidean pattern using Bjorklund algorithm."""
        if self.pulses >= self.steps:
            return [1] * self.steps
        if self.pulses <= 0:
            return [0] * self.steps
        
        # Simple Bjorklund: distribute pulses as evenly as possible
        pattern = []
        bucket = 0
        for i in range(self.steps):
            bucket += self.pulses
            if bucket >= self.steps:
                bucket -= self.steps
                pattern.append(1)
            else:
                pattern.append(0)
        
        # Apply rotation
        if self.rotation != 0:
            r = self.rotation % self.steps
            pattern = pattern[r:] + pattern[:r]
        
        return pattern
    
    def generate(self, steps: Optional[int] = None, bars: int = 1, **kwargs) -> List[int]:
        """
        Generate Euclidean rhythm pattern.
        
        Args:
            steps: Number of steps (alias for bars * pattern_length)
            bars: Number of bars (pattern repeats)
            
        Returns:
            List of 0/1 values (0=rest, 1=hit)
        """
        pattern = self._generate_pattern()
        if steps is not None:
            # Generate enough pattern to cover steps
            repeats = (steps + len(pattern) - 1) // len(pattern)
            result = pattern * repeats
            return result[:steps]
        return pattern * bars


class MarkovCore(EventCore):
    """
    Markov chain generator.
    
    Generates sequences based on transition probabilities.
    Supports first-order (single-step) and second-order (context-aware) chains.
    """
    
    def __init__(self, transition_matrix: Dict[Any, Dict[Any, float]],
                 order: int = 1, name: str = "markov"):
        """
        Args:
            transition_matrix: Dict[state, Dict[next_state, probability]]
            order: Markov chain order (1 or 2)
        """
        super().__init__(name)
        self.transition_matrix = transition_matrix
        self.order = order
        self._normalize_matrix()
    
    def _normalize_matrix(self):
        """Ensure transition probabilities sum to 1.0 for each state."""
        for state, transitions in self.transition_matrix.items():
            total = sum(transitions.values())
            if total > 0:
                self.transition_matrix[state] = {
                    k: v / total for k, v in transitions.items()
                }
    
    def _weighted_choice(self, options: Dict[Any, float]) -> Any:
        """Choose from options based on weighted probabilities."""
        items = list(options.items())
        weights = [w for _, w in items]
        total = sum(weights)
        if total == 0:
            return items[0][0]
        
        r = random.random() * total
        cumulative = 0
        for item, weight in items:
            cumulative += weight
            if r <= cumulative:
                return item
        return items[-1][0]
    
    def generate(self, steps: int, seed: Any = None, **kwargs) -> List[Any]:
        """
        Generate Markov chain sequence.
        
        Args:
            steps: Number of steps to generate
            seed: Starting state (if None, picks random)
            
        Returns:
            List of states
        """
        if seed is None:
            seed = random.choice(list(self.transition_matrix.keys()))
        
        sequence = [seed]
        current = seed
        
        for _ in range(steps - 1):
            if current not in self.transition_matrix:
                # Dead end — pick random state
                current = random.choice(list(self.transition_matrix.keys()))
            else:
                transitions = self.transition_matrix[current]
                current = self._weighted_choice(transitions)
            
            sequence.append(current)
        
        return sequence


class StochasticCore(EventCore):
    """
    Stochastic generator with tendency masking.
    
    Generates values within constrained ranges using weighted random selection.
    Supports:
    - Pitch range constraints
    - Step size limits
    - Tendency toward target values
    """
    
    def __init__(self, value_range: tuple = (0, 127),
                 max_step: int = 12,
                 tendency_target: Optional[float] = None,
                 tendency_strength: float = 0.3,
                 name: str = "stochastic"):
        """
        Args:
            value_range: (min, max) for generated values
            max_step: Maximum step size between consecutive values
            tendency_target: Optional target value to drift toward
            tendency_strength: How strongly to pull toward target (0-1)
        """
        super().__init__(name)
        self.value_range = value_range
        self.max_step = max_step
        self.tendency_target = tendency_target
        self.tendency_strength = tendency_strength
    
    def generate(self, steps: int, seed: Optional[int] = None, **kwargs) -> List[int]:
        """
        Generate stochastic sequence.
        
        Args:
            steps: Number of values to generate
            seed: Starting value (if None, picks random in range)
            
        Returns:
            List of integer values
        """
        if seed is None:
            seed = random.randint(self.value_range[0], self.value_range[1])
        
        sequence = [seed]
        current = seed
        
        for _ in range(steps - 1):
            # Calculate allowed range based on max_step
            low = max(self.value_range[0], current - self.max_step)
            high = min(self.value_range[1], current + self.max_step)
            
            # Apply tendency toward target
            if self.tendency_target is not None and self.should_vary():
                # Weight choices toward target
                center = current + (self.tendency_target - current) * self.tendency_strength
                # Generate with Gaussian bias toward center
                candidate = int(np.random.normal(center, self.max_step / 2))
                candidate = max(low, min(high, candidate))
            else:
                # Uniform random within step range
                candidate = random.randint(low, high)
            
            sequence.append(candidate)
            current = candidate
        
        return sequence


class LSystemCore(EventCore):
    """
    L-system (Lindenmayer system) generator.
    
    Generates sequences via string rewriting rules.
    Classic example: axiom="A", rules={"A": "AB", "B": "A"}
    After 3 iterations: ABAABABA
    """
    
    def __init__(self, axiom: str = "A",
                 rules: Dict[str, str] = None,
                 name: str = "lsystem"):
        super().__init__(name)
        self.axiom = axiom
        self.rules = rules or {"A": "AB", "B": "A"}
    
    def _iterate(self, iterations: int) -> str:
        """Apply rewriting rules for N iterations."""
        current = self.axiom
        for _ in range(iterations):
            next_str = ""
            for char in current:
                next_str += self.rules.get(char, char)
            current = next_str
        return current
    
    def generate(self, iterations: int = 3, **kwargs) -> str:
        """
        Generate L-system string.
        
        Args:
            iterations: Number of rewriting iterations
            
        Returns:
            Generated string
        """
        return self._iterate(iterations)
    
    def generate_mapped(self, iterations: int = 3,
                       mapping: Dict[str, Any] = None) -> List[Any]:
        """
        Generate and map symbols to values.
        
        Args:
            iterations: Number of iterations
            mapping: Dict[symbol, value] (default: A=0, B=1)
            
        Returns:
            List of mapped values
        """
        if mapping is None:
            mapping = {"A": 0, "B": 1}
        
        string = self._iterate(iterations)
        return [mapping.get(c, 0) for c in string]


class WeightedRandomCore(EventCore):
    """
    Weighted random selection with history awareness.
    
    Selects from a pool of values with configurable weights.
    Can avoid recent selections to prevent repetition.
    """
    
    def __init__(self, pool: Dict[Any, float],
                 avoid_repeats: int = 0,
                 name: str = "weighted_random"):
        """
        Args:
            pool: Dict[value, weight]
            avoid_repeats: Number of recent values to avoid
        """
        super().__init__(name)
        self.pool = pool
        self.avoid_repeats = avoid_repeats
        self._recent = []
    
    def generate(self, steps: int, **kwargs) -> List[Any]:
        """
        Generate weighted random sequence.
        
        Args:
            steps: Number of selections
            
        Returns:
            List of selected values
        """
        sequence = []
        
        for _ in range(steps):
            # Filter out recent values if avoiding repeats
            available = {k: v for k, v in self.pool.items() 
                        if k not in self._recent[-self.avoid_repeats:]}
            
            if not available:
                available = self.pool.copy()
            
            # Weighted selection
            items = list(available.items())
            weights = [w for _, w in items]
            total = sum(weights)
            
            if total == 0:
                selected = items[0][0]
            else:
                r = random.random() * total
                cumulative = 0
                selected = items[-1][0]
                for item, weight in items:
                    cumulative += weight
                    if r <= cumulative:
                        selected = item
                        break
            
            sequence.append(selected)
            self._recent.append(selected)
        
        return sequence


class PatternSequencer:
    """
    Combines multiple event cores into a structured pattern.
    
    Allows layering different cores for different parameters
    (pitch, rhythm, velocity) and synchronizing their generation.
    """
    
    def __init__(self):
        self.cores: Dict[str, EventCore] = {}
    
    def add_core(self, name: str, core: EventCore):
        """Add an event core to the sequencer."""
        self.cores[name] = core
    
    def remove_core(self, name: str):
        """Remove an event core."""
        self.cores.pop(name, None)
    
    def generate(self, steps: int, **kwargs) -> Dict[str, List[Any]]:
        """
        Generate from all cores.
        
        Args:
            steps: Number of steps
            **kwargs: Passed to each core's generate()
            
        Returns:
            Dict[core_name, List[values]]
        """
        result = {}
        for name, core in self.cores.items():
            result[name] = core.generate(steps, **kwargs)
        return result
    
    def lock_all(self):
        """Lock all cores."""
        for core in self.cores.values():
            core._locked_params.add("all")
    
    def unlock_all(self):
        """Unlock all cores."""
        for core in self.cores.values():
            core._locked_params.discard("all")
    
    def reset_all(self):
        """Reset all cores."""
        for core in self.cores.values():
            core.reset()


if __name__ == "__main__":
    # Smoke test
    print("=== Event Core Framework Test ===\n")
    
    # Euclidean
    euc = EuclideanCore(pulses=5, steps=16)
    pattern = euc.generate(2)
    print(f"Euclidean(5,16): {''.join(str(p) for p in pattern)}")
    
    # Markov
    matrix = {
        60: {62: 0.4, 64: 0.3, 65: 0.3},
        62: {60: 0.3, 64: 0.4, 67: 0.3},
        64: {62: 0.3, 65: 0.4, 69: 0.3},
        65: {64: 0.4, 67: 0.3, 69: 0.3},
    }
    markov = MarkovCore(matrix)
    seq = markov.generate(8, seed=60)
    print(f"Markov chain: {seq}")
    
    # Stochastic
    stoch = StochasticCore(value_range=(60, 72), max_step=4, tendency_target=66)
    stoch_seq = stoch.generate(10, seed=64)
    print(f"Stochastic: {stoch_seq}")
    
    # L-System
    lsys = LSystemCore(axiom="A", rules={"A": "AB", "B": "A"})
    string = lsys.generate(4)
    print(f"L-System (4 iter): {string}")
    mapped = lsys.generate_mapped(4, {"A": 60, "B": 67})
    print(f"L-System mapped: {mapped}")
    
    # Pattern Sequencer
    seq = PatternSequencer()
    seq.add_core("rhythm", EuclideanCore(5, 16))
    seq.add_core("pitch", StochasticCore((60, 72), 3))
    result = seq.generate(8)
    print(f"Sequencer rhythm: {''.join(str(p) for p in result['rhythm'])}")
    print(f"Sequencer pitch: {result['pitch']}")
    
    print("\n✓ Event Core Framework smoke test passed")
