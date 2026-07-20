import random
from typing import List, Dict, Any, Tuple, Optional
from structures.unit import MusicEvent, MusicUnit

class MarkovConstraintGenerator:
    """
    Method 022: Markov-Constraint Wavefront Sequencing (MCWS)
    Generates pitch sequences by satisfying probabilistic local state transitions
    while validating and honoring global voice range and scale constraints.
    """
    
    def __init__(self, key_pitches: List[int], default_pitch: int = 60, min_pitch: int = 36, max_pitch: int = 84):
        """
        Initialize MCWS with scale bounds.
        """
        self.key_pitches = key_pitches
        self.default_pitch = default_pitch
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        
        self.transitions: Dict[int, List[int]] = {}
        for p in self.key_pitches:
            self.transitions[p] = [
                n for n in self.key_pitches 
                if abs(n - p) <= 7 and self.min_pitch <= n <= self.max_pitch
            ]
            if not self.transitions[p]:
                self.transitions[p] = [p]

    def generate_voice_section(self, section_ticks: int, step_ticks: int, 
                              previous_pitch: Optional[int] = None, 
                              density: float = 0.7, 
                              volume: int = 90) -> MusicUnit:
        events: List[MusicEvent] = []
        curr_tick = 0
        curr_pitch = previous_pitch if previous_pitch in self.key_pitches else random.choice(self.key_pitches)
        
        while curr_tick < section_ticks:
            step = step_ticks
            if curr_tick + step > section_ticks:
                step = section_ticks - curr_tick
                
            if random.random() < density:
                candidates = self.transitions.get(curr_pitch, self.key_pitches)
                if not candidates:
                    candidates = self.key_pitches
                    
                valid_candidates = [c for c in candidates if self.min_pitch <= c <= self.max_pitch]
                if not valid_candidates:
                    valid_candidates = [self.default_pitch]
                    
                next_pitch = random.choice(valid_candidates)
                
                events.append(MusicEvent(
                    pitch=next_pitch, 
                    volume=volume, 
                    start_tick=curr_tick, 
                    end_tick=curr_tick + step - min(40, step // 4)
                ))
                curr_pitch = next_pitch
            curr_tick += step
            
        # Ensure the MusicUnit length matches exactly the section duration by adding a silent terminal landmark
        if events:
            # If the last event ends before the section boundary, append a dummy structural landmark
            if events[-1].end_tick < section_ticks:
                events.append(MusicEvent(pitch=0, volume=0, start_tick=events[-1].end_tick, end_tick=section_ticks))
        else:
            events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks))
            
        return MusicUnit(events=events)
