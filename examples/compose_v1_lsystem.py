import sys
import os

# Set up path discovery
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from structures import MusicUnit, MusicEvent

def get_diatonic_note(key_root: int, scale_intervals: list, degree_index: int) -> int:
    octave_shift = degree_index // 7
    scale_step = degree_index % 7
    return key_root + (octave_shift * 12) + scale_intervals[scale_step]

def compose_l_system_32bars():
    print("=== COMPOSITION 1: METHOD SP-019 (L-SYSTEM MELODIC GROWTH) ===")
    
    # 32 Bars total @ 120 BPM
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("L-System Lead", program=81, channel=0)
    pad_row = composer.add_voice("L-System Pad", program=89, channel=1)
    bass_row = composer.add_voice("L-System Bass", program=38, channel=2)
    perc_row = composer.add_voice("L-System Perc", program=0, channel=9)
    
    sec_intro = composer.add_section("Intro", bars=8)
    sec_verse = composer.add_section("Verse", bars=8)
    sec_chorus = composer.add_section("Chorus", bars=8)
    sec_outro = composer.add_section("Outro", bars=8)
    
    # L-System Grammar Rules:
    # Axiom: F
    # Rule: F -> F+F-F+F
    # 3 Iterations
    state = "F"
    rule = "F+F-F+F"
    for _ in range(2):  # Limit to 2 iterations for clean 32-bar mapping
        next_state = ""
        for char in state:
            if char == 'F':
                next_state += rule
            else:
                next_state += char
        state = next_state
        
    print(f"L-System String Sequence: {state}")
    
    # A Minor scale
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 8, 10]
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Intro", sec_intro), ("Verse", sec_verse), ("Chorus", sec_chorus), ("Outro", sec_outro)]
    
    # Chord degrees
    chords_map = {
        "Intro": [0, 0, 0, 0],
        "Verse": [0, 3, 6, 2],
        "Chorus": [5, 6, 4, 0],
        "Outro": [0, 3, 4, 0]
    }
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = chords_map[sec_name]
        
        # 1. Lead Generation based on L-System String Mapping
        lead_events = []
        tick = 0
        char_idx = 0
        scale_degree = 0  # Starting relative offset
        
        step_ticks = 480  # quarter note steps
        while tick < total_section_ticks:
            char = state[char_idx % len(state)]
            char_idx += 1
            
            if char == 'F':
                # Emit a note relative to the current bar's chord root
                current_bar = tick // ticks_per_bar
                chord_root_deg = degrees[current_bar % 4]
                pitch = get_diatonic_note(key_root, scale_intervals, chord_root_deg + scale_degree) + 12
                
                end_t = tick + step_ticks
                if end_t > total_section_ticks:
                    end_t = total_section_ticks
                    
                lead_events.append(MusicEvent(pitch=pitch, volume=85, start_tick=tick, end_tick=end_t))
                tick += step_ticks
            elif char == '+':
                scale_degree += 1  # Shift relative scale vector Up
            elif char == '-':
                scale_degree -= 1  # Shift relative scale vector Down
                
        # Enforce final padding rest note at the absolute boundary of the lead track
        lead_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Support Pad
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            r = get_diatonic_note(key_root, scale_intervals, root_deg)
            t = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            f = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            pad_events.append(MusicEvent(pitch=r, volume=70, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=t, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=f, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Bass
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
            half_bar = ticks_per_bar // 2
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start, end_tick=bar_start + half_bar))
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start + half_bar, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Percussion
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            perc_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + (half_bar // 2), end_tick=bar_start + half_bar))
            perc_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + (half_bar + (half_bar // 2)), end_tick=bar_start + ticks_per_bar))
            # hi-hat patterns
            for hh in range(0, ticks_per_bar, 240):
                perc_events.append(MusicEvent(pitch=42, volume=70, start_tick=bar_start + hh, end_tick=bar_start + hh + 120))
            # strict timing pad
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment error: {err}")
        sys.exit(1)
    
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/composition1_lsystem.mid"
    composer.to_midi(midi_path)
    print(f"L-System Composition MIDI exported => {midi_path}")

if __name__ == "__main__":
    compose_l_system_32bars()
