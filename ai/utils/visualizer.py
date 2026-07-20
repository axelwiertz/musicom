import sys
import os
import numpy as np

# Ensure repository path is loaded
sys.path.insert(0, "/opt/data/repos/musicom")

from structures.matrix import UnitMatrix
from structures.unit import MusicUnit, MusicEvent

def print_high_contrast_grid(matrix: UnitMatrix, ticks_per_character: int = 120):
    """
    Renders an interactive-style high-contrast terminal ascii grid showing
    notes alignment, density, and overlaps across voices (rows) and sections (columns).
    Prints: █ for note onsets/sustain, ░ for rests/silence.
    """
    print("=" * 70)
    print("MUSICOM UNITMATRIX VISUALIZER (HIGH-CONTRAST TIMELINE)")
    print(f"Matrix shape: {matrix.num_rows} rows (voices) × {matrix.num_cols} cols (sections)")
    print("=" * 70)
    
    # Pre-calculate absolute timing boundaries per section
    # Let's inspect the cells
    # First, find total duration of each section column
    col_durations = []
    for c in range(matrix.num_cols):
        max_tick = 0
        for r in range(matrix.num_rows):
            unit = matrix.get_unit((r, c))
            if unit is not None and len(unit.data) > 0:
                # Find maximum tick in this cell
                for e in unit.events:
                    if e.end_tick > max_tick:
                        max_tick = e.end_tick
        col_durations.append(max_tick if max_tick > 0 else 480 * 4) # default fallback to 4 beats
        
    print(f"Section Durations (ticks): {col_durations}")
    print("-" * 70)

    for r in range(matrix.num_rows):
        row_str = f"Voice {r:02d} |"
        for c in range(matrix.num_cols):
            unit = matrix.get_unit((r, c))
            cell_dur = col_durations[c]
            num_chars = max(1, int(cell_dur / ticks_per_character))
            
            # Map of characters for this cell
            # Init empty
            grid_chars = ["░"] * num_chars
            
            if unit is not None and len(unit.data) > 0:
                for e in unit.events:
                    start_char = int(e.start_tick / ticks_per_character)
                    end_char = int(e.end_tick / ticks_per_character)
                    # boundary checks
                    start_char = max(0, min(start_char, num_chars - 1))
                    end_char = max(start_char + 1, min(end_char, num_chars))
                    
                    for idx in range(start_char, end_char):
                        grid_chars[idx] = "█"
            
            row_str += "".join(grid_chars) + " |"
        print(row_str)
        
    print("-" * 70)
    print("Legend: █ = Sounding Event | ░ = Silence/Rest | | = Section Boundary")
    print("=" * 70)

if __name__ == "__main__":
    # Self-test build with mock matrix
    print("Self-test visualizer:")
    events_v1_s1 = [MusicEvent(60, 100, 0, 240), MusicEvent(62, 100, 240, 480)]
    events_v1_s2 = [MusicEvent(64, 100, 0, 480)]
    events_v2_s1 = [MusicEvent(48, 100, 0, 480)]
    events_v2_s2 = [] # Rest
    
    u11 = MusicUnit(events=events_v1_s1)
    u12 = MusicUnit(events=events_v1_s2)
    u21 = MusicUnit(events=events_v2_s1)
    u22 = MusicUnit(events=events_v2_s2)
    
    m = UnitMatrix(shape=(2, 2))
    m.set_unit((0,0), u11)
    m.set_unit((0,1), u12)
    m.set_unit((1,0), u21)
    m.set_unit((1,1), u22)
    
    print_high_contrast_grid(m, ticks_per_character=60)
