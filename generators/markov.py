import random
from typing import List, Dict, Any
from structures.unit import MusicEvent

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
        if len(events) <= self.order:
            return

        pitches = [e.pitch for e in events if e.pitch > 0]
        durations = [e.duration for e in events]

        self._build_chain(pitches, self.pitch_chain)
        self._build_chain(durations, self.duration_chain)

    def _build_chain(self, sequence: List[Any], chain: Dict[tuple, List[Any]]):
        for i in range(len(sequence) - self.order):
            state = tuple(sequence[i:i + self.order])
            next_val = sequence[i + self.order]
            if state not in chain:
                chain[state] = []
            chain[state].append(next_val)

    def generate(self, length: int, start_state: tuple = None) -> List[Dict[str, int]]:
        if not self.pitch_chain or not self.duration_chain:
            return []

        if start_state is None or start_state not in self.pitch_chain:
            start_state = random.choice(list(self.pitch_chain.keys()))

        current_pitch_state = start_state
        current_dur_state = random.choice(list(self.duration_chain.keys()))

        output = []
        for _ in range(length):
            # Pitch transition
            next_pitches = self.pitch_chain.get(current_pitch_state)
            if not next_pitches:
                next_pitch = random.choice(list(self.pitch_chain.keys()))[0]
            else:
                next_pitch = random.choice(next_pitches)

            # Duration transition
            next_durs = self.duration_chain.get(current_dur_state)
            if not next_durs:
                next_dur = random.choice(list(self.duration_chain.keys()))[0]
            else:
                next_dur = random.choice(next_durs)

            output.append({"pitch": next_pitch, "duration": next_dur})

            # Update states
            current_pitch_state = tuple(list(current_pitch_state[1:]) + [next_pitch])
            current_dur_state = tuple(list(current_dur_state[1:]) + [next_dur])

        return output
