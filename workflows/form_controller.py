"""Macro-structural Form Planning Engine.

This module maps macro-level emotional and narrative tension curves (0.0 to 1.0)
directly to programmatic generator bounds within the UnitMatrix.
"""

from typing import List, Dict, Any, Tuple

class FormPlanController:
    """Calculates generative thresholds relative to a global tension curve."""
    
    def __init__(self, key_center: str = "C", scale_name: str = "major"):
        self.key_center = key_center
        self.scale_name = scale_name
        self.sections: List[Dict[str, Any]] = []
        
    def add_section(self, name: str, bars: int, start_tension: float, end_tension: float):
        """Add a section to the structural form layout."""
        self.sections.append({
            "name": name,
            "bars": bars,
            "tension_range": (start_tension, end_tension)
        })
        
    def get_tension_for_bar(self, target_section_name: str, bar_index: int) -> float:
        """Interpolate the precise tension point for a specific bar inside a section."""
        section = next((s for s in self.sections if s["name"] == target_section_name), None)
        if not section:
            return 0.5
            
        start_t, end_t = section["tension_range"]
        total_bars = section["bars"]
        
        if total_bars <= 1:
            return start_t
            
        progress = bar_index / (total_bars - 1)
        return start_t + progress * (end_t - start_t)
        
    def get_generative_bounds(self, section_name: str, bar_index: int) -> Dict[str, Any]:
        """Convert a tension coefficient into concrete generator parameters."""
        tension = self.get_tension_for_bar(section_name, bar_index)
        
        # Mapping rules based on absolute tension levels
        # 1. Rhythm density increases as tension increases
        density_rate = 1.0 + (tension * 3.0)  # ranges from 1.0 (sparse) to 4.0 (busy)
        
        # 2. Pitch register boundaries expand as tension climbs
        pitch_dispersion = int(12 + (tension * 24))  # dispersion ranges from 1 octave to 3 octaves
        
        # 3. Micro-detuning and humanization offsets (simulates performance urgency)
        humanization_drift_ticks = int(2 + (tension * 15))  # more tension -> slightly wider expressive drift
        
        return {
            "tension": tension,
            "density_rate": density_rate,
            "pitch_dispersion": pitch_dispersion,
            "humanization_drift": humanization_drift_ticks
        }
