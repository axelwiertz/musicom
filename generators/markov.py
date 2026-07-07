import random
from typing import List, Dict, Any
from musicom.structures.unit import MusicEvent

class MarkovGenerator:
    """
    Simple Markov Chain generator for musical events.
    Learns transitions between pitches and durations.
    """
    def __init__(self, order: int = 1):
        self.order = order
        self.pitch_chain: Dict[tuple, List[int]] = {}
        self.duration_chain: Dict[tuple, List[int]] = {}

    def train(self, events: List[MusicEvent]):
        """Train the chain on a sequence of MusicEvents."""
        pitches = [e.pitch for e in events if e.pitch is not None]
        durations = [e.duration for e in events]

        self._build_chain(pitches, self.pitch_chain)
        self._build_chain(durations, self.duration_chain)

    def _build_chain(self, sequence: List[Any], chain: Dict[tuple, List[Any]]):
        if len(sequence) <= self.order:
            return

        for i in range(len(sequence) - self.order):
            state = tuple(sequence[i : i + self.order])
            next_val = sequence[i + self.order]
            if state not in chain:
                chain[state] = []
            chain[state].append(next_val)

    def generate(self, length: int, start_state: tuple = None) -> List[Dict[str, int]]:
        """Generate a new sequence of pitch/duration dicts."""
        if not self.pitch_chain or not self.duration_chain:
            raise ValueError("Chain not trained.")

        # Pick random start if none provided
        if not start_state:
            start_state = random.choice(list(self.pitch_chain.keys()))

        current_pitch_state = start_state
        current_dur_state = random.choice(list(self.duration_chain.keys()))
        
        output = []
        for _ in range(length):
            next_pitch = random.choice(self.pitch_chain.get(current_pitch_state, list(sum(self.pitch_chain.values(), []))))
            next_dur = random.choice(self.duration_chain.get(current_dur_state, list(sum(self.duration_chain.values(), []))))
            
            output.append({"pitch": next_pitch, "duration": next_dur})
            
            current_pitch_state = current_pitch_state[1:] + (next_pitch,)
            current_dur_state = current_dur_state[1:] + (next_dur,)
            
        return output
