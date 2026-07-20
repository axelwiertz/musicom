import random
from typing import List, Tuple
from structures.unit import MusicEvent, MusicUnit

class TendencyMaskingGenerator:
    """
    Method 023: Tendency Masking Stochastic Bounds
    Restricts stochastic pitch generation within dynamic upper and lower frequency envelopes over time.
    """
    
    def __init__(self, key_pitches: List[int]):
        self.key_pitches = key_pitches

    def generate_voice_section(self, section_ticks: int, step_ticks: int, 
                              bounds_start: Tuple[int, int], bounds_end: Tuple[int, int], 
                              density: float = 0.8, volume: int = 85) -> MusicUnit:
        events: List[MusicEvent] = []
        curr_tick = 0
        
        while curr_tick < section_ticks:
            step = step_ticks
            if curr_tick + step > section_ticks:
                step = section_ticks - curr_tick
                
            progress = curr_tick / section_ticks
            lower_bound = bounds_start[0] + progress * (bounds_end[0] - bounds_start[0])
            upper_bound = bounds_start[1] + progress * (bounds_end[1] - bounds_start[1])
            
            if random.random() < density:
                in_bounds_pitches = [p for p in self.key_pitches if lower_bound <= p <= upper_bound]
                
                if in_bounds_pitches:
                    pitch = random.choice(in_bounds_pitches)
                    events.append(MusicEvent(
                        pitch=pitch,
                        volume=volume,
                        start_tick=curr_tick,
                        end_tick=curr_tick + step - min(40, step // 4)
                    ))
            curr_tick += step
            
        # Ensure the MusicUnit length matches exactly the section duration by adding a silent terminal landmark
        if events:
            if events[-1].end_tick < section_ticks:
                events.append(MusicEvent(pitch=0, volume=0, start_tick=events[-1].end_tick, end_tick=section_ticks))
        else:
            events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks))
            
        return MusicUnit(events=events)
