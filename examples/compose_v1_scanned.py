import sys
import os
import numpy as np

# Set up path discovery
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from structures import MusicUnit, MusicEvent

def get_diatonic_note(key_root: int, scale_intervals: list, degree_index: int) -> int:
    octave_shift = degree_index // 7
    scale_step = degree_index % 7
    return key_root + (octave_shift * 12) + scale_intervals[scale_step]

def compose_scanned_synthesis_32bars():
    print("=== COMPOSITION 1: METHOD SP-018 (SCANNED SYNTHESIS ENGINE) ===")
    print("Core Concept: Slow physical model (mass-spring string) scanned at audio rate to drive dynamic wavetable shapes")
    
    # 32 Bars total @ 120 BPM
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Scanned Lead", program=81, channel=0)
    pad_row = composer.add_voice("Scanned Pad", program=89, channel=1)
    bass_row = composer.add_voice("Scanned Bass", program=38, channel=2)
    perc_row = composer.add_voice("Scanned Perc", program=0, channel=9)
    
    sec_intro = composer.add_section("Intro", bars=8)
    sec_verse = composer.add_section("Verse", bars=8)
    sec_chorus = composer.add_section("Chorus", bars=8)
    sec_outro = composer.add_section("Outro", bars=8)
    
    # Simulating a physical Scanned Synthesis String (Mass-Spring Lattice)
    # Mass displacement array x, velocity v, and spring constants
    num_masses = 16
    string_x = np.sin(np.linspace(0, np.pi, num_masses)) * 0.5  # Init displacement (sinusoidal pluck)
    string_v = np.zeros(num_masses)
    
    k_s = 0.4  # spring coupling constant
    damping = 0.985
    
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural Minor
    
    chords_map = {
        "Intro": [0, 0, 0, 0],
        "Verse": [0, 3, 6, 2],
        "Chorus": [5, 6, 4, 0],
        "Outro": [0, 3, 4, 0]
    }
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Intro", sec_intro), ("Verse", sec_verse), ("Chorus", sec_chorus), ("Outro", sec_outro)]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = chords_map[sec_name]
        print(f"Executing mass-spring scanned synthesis updates for [{sec_name}]...")
        
        # 1. Lead Generation based on the Scanned Wavetable state
        lead_events = []
        tick = 0
        step_ticks = 480  # quarter notes
        
        while tick < total_section_ticks:
            # Physical mass-spring integration step:
            # a_i = k_s * (x_{i+1} - 2x_i + x_{i-1})
            # v_i = (v_i + a_i) * damping
            # x_i = x_i + v_i
            accel = np.zeros(num_masses)
            for i in range(1, num_masses - 1):
                accel[i] = k_s * (string_x[i+1] - 2 * string_x[i] + string_x[i-1])
            string_v = (string_v + accel) * damping
            string_x = string_x + string_v
            
            # Map the average displacement shape of the scanned string to a dynamic pitch degree
            avg_displacement = np.mean(np.abs(string_x))
            pitch_offset = int(avg_displacement * 12)  # Pitch contour fluctuates organically as spring energy decays
            
            current_bar = tick // ticks_per_bar
            chord_root_deg = degrees[current_bar % 4]
            pitch = get_diatonic_note(key_root, scale_intervals, chord_root_deg + (tick // step_ticks) % 4) + 12 + pitch_offset
            
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            lead_events.append(MusicEvent(pitch=pitch, volume=int(80 + (avg_displacement * 40)), start_tick=tick, end_tick=end_t))
            tick += step_ticks
            
            # Periodically re-excite (pluck) the scanned string to keep energy alive
            if tick % ticks_per_bar == 0:
                string_x += np.sin(np.linspace(0, np.pi, num_masses)) * 0.4
                
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
            for hh in range(0, ticks_per_bar, 240):
                perc_events.append(MusicEvent(pitch=42, volume=70, start_tick=bar_start + hh, end_tick=bar_start + hh + 120))
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment error: {err}")
        sys.exit(1)
        
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/composition1_scanned.mid"
    composer.to_midi(midi_path)
    print(f"Scanned Synthesis Composition MIDI exported => {midi_path}")

if __name__ == "__main__":
    compose_scanned_synthesis_32bars()
