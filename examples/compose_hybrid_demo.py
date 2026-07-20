import sys
import os
import numpy as np

# Set up path discovery
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.form_controller import FormPlanController
from structures import MusicUnit, MusicEvent

def get_diatonic_note(key_root: int, scale_intervals: list, degree_index: int) -> int:
    octave_shift = degree_index // 7
    scale_step = degree_index % 7
    return key_root + (octave_shift * 12) + scale_intervals[scale_step]

def compose_chaotic_harmonic_hybrid():
    print("=== INITIALIZING CHAOTIC-HARMONIC HYBRID COMPOSITION (32 BARS) ===")
    print("Core Concept: Smoothing chaotic Hénon attractor grains using strict diatonic harmonic rules")
    
    # 32 Bars total @ 120 BPM
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Hybrid Lead", program=73, channel=0)      # Flute (Classic, smooth)
    pad_row = composer.add_voice("Hybrid Pad", program=48, channel=1)        # Orchestral Strings
    bass_row = composer.add_voice("Hybrid Bass", program=43, channel=2)      # Double Bass
    perc_row = composer.add_voice("Hybrid Perc", program=0, channel=9)       # Percussion Channel 10
    
    # Define 4 sections (8 bars each)
    sec_intro = composer.add_section("Intro", bars=8)
    sec_verse = composer.add_section("Verse", bars=8)
    sec_chorus = composer.add_section("Chorus", bars=8)
    sec_outro = composer.add_section("Outro", bars=8)
    
    # Natural Minor Scale (A Minor) - strict diatonic smoothing grid
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 8, 10]
    
    # Harmonic progression skeleton (0-indexed scale degrees):
    # Intro:  i - i - i - i (0 - 0 - 0 - 0)
    # Verse:  i - iv - bVII - bIII (0 - 3 - 6 - 2)
    # Chorus: bVI - bVII - v - i (5 - 6 - 4 - 0)
    # Outro:  i - iv - v - i (0 - 3 - 4 - 0)
    progression_blueprint = {
        "Intro": [0, 0, 0, 0],
        "Verse": [0, 3, 6, 2],
        "Chorus": [5, 6, 4, 0],
        "Outro": [0, 3, 4, 0]
    }
    
    # Hénon Attractor variables
    a, b = 1.4, 0.3
    x, y = 0.1, 0.1
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Intro", sec_intro), ("Verse", sec_verse), ("Chorus", sec_chorus), ("Outro", sec_outro)]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = progression_blueprint[sec_name]
        print(f"Synthesizing smoothed chaotic-harmonic cells for [{sec_name}]...")
        
        # 1. Lead Generation: Chaotic Hénon attractor grain times, smoothed via strict diatonic scale degrees
        lead_events = []
        tick = 0
        while tick < total_section_ticks:
            next_x = 1 - a * (x ** 2) + y
            next_y = b * x
            x, y = next_x, next_y
            
            norm_x = (x + 1.2) / 2.4
            norm_x = np.clip(norm_x, 0.05, 1.0)
            
            # Grain duration remains organic/chaotic (between 16th and half notes)
            grain_duration = int(120 + (norm_x * 960))
            
            # Map the raw chaotic coordinate to a DIATONIC degree offset relative to the chord root
            current_bar = tick // ticks_per_bar
            chord_root_deg = degrees[current_bar % 4]
            
            # Offset degree index based on chaotic state (clamped to chord tones: root, 3rd, 5th, 7th)
            chaotic_chord_offset = int(norm_x * 4) * 2  # yields 0, 2, 4, or 6 scale steps above chord root
            target_deg = chord_root_deg + chaotic_chord_offset
            
            pitch = get_diatonic_note(key_root, scale_intervals, target_deg) + 12
            
            end_tick = tick + grain_duration
            if end_tick > total_section_ticks:
                end_tick = total_section_ticks
                
            lead_events.append(MusicEvent(pitch=pitch, volume=int(70 + (norm_x * 40)), start_tick=tick, end_tick=end_tick))
            tick += grain_duration
            
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Pad Generation (Strict diatonic triad voicing)
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg)
            third_pitch = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            fifth_pitch = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            
            pad_events.append(MusicEvent(pitch=root_pitch, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=third_pitch, volume=60, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=fifth_pitch, volume=60, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Bass Generation (Voice leading: Root & Fifth movement)
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
            fifth_pitch = get_diatonic_note(key_root, scale_intervals, root_deg + 4) - 12
            
            half_bar = ticks_per_bar // 2
            bass_events.append(MusicEvent(pitch=root_pitch, volume=80, start_tick=bar_start, end_tick=bar_start + half_bar))
            bass_events.append(MusicEvent(pitch=fifth_pitch, volume=75, start_tick=bar_start + half_bar, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Percussion (Backing metronome + chaotic hi-hat triggers)
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            
            # Classical snare metronome pulse
            perc_events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_start + half_bar, end_tick=bar_start + half_bar + 240))
            
            # Chaotic hi-hat triggers (retained from original CMCG, adds organic friction)
            for hh_tick in range(0, ticks_per_bar, 240):
                next_x = 1 - a * (x ** 2) + y
                x, y = next_x, b * x
                if x > 0.1:
                    perc_events.append(MusicEvent(pitch=42, volume=65, start_tick=bar_start + hh_tick, end_tick=bar_start + hh_tick + 120))
                    
            # Boundary padding
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment validation failed: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/chaotic_harmonic_hybrid.mid"
    composer.to_midi(midi_path)
    print(f"Hybrid MIDI written to => {midi_path}")

if __name__ == "__main__":
    compose_chaotic_harmonic_hybrid()
