import sys
import os
import numpy as np

# Set up path discovery
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.form_controller import FormPlanController
from structures import MusicUnit, MusicEvent

def compose_cmcg_32bars():
    print("=== INITIALIZING CHAOTICALLY MODULATED CELLULAR GRAINS (CMCG) ENSEMBLE ===")
    print("Method ID: 028 | Paradigm: Nature-Led")
    
    # 32 Bars total @ 125 BPM
    composer = UnitMatrixComposer(bpm=125, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Grain Lead", program=80, channel=0)      # Square Lead (Chirpy)
    pad_row = composer.add_voice("Cloud Pad", program=91, channel=1)        # Pad PolySynth (Diffuse)
    bass_row = composer.add_voice("Stoch Bass", program=39, channel=2)      # Synth Bass (Driving)
    perc_row = composer.add_voice("Chaos Perc", program=0, channel=9)       # Percussion Channel 10
    
    # Divide 32 bars into 4 large sections (8 bars each)
    sec_a = composer.add_section("A_Phase", bars=8)
    sec_b = composer.add_section("B_Phase", bars=8)
    sec_c = composer.add_section("C_Phase", bars=8)
    sec_d = composer.add_section("D_Phase", bars=8)
    
    # Hénon Attractor Chaotic Equation State:
    # x_{n+1} = 1 - a * x_n^2 + y_n
    # y_{n+1} = b * x_n
    a, b = 1.4, 0.3
    x, y = 0.1, 0.1  # Attractor seed
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("A_Phase", sec_a), ("B_Phase", sec_b), ("C_Phase", sec_c), ("D_Phase", sec_d)]
    
    # Absolute scale map: A Phrygian (A, Bb, C, D, E, F, G) for chaotic dissonance control
    scale_steps = [57, 58, 60, 62, 64, 65, 67]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        print(f"Synthesizing chaotic grain cells for [{sec_name}] over {bars_count} bars ({total_section_ticks} ticks)...")
        
        # 1. Grain Lead Generation (Chaotic Inter-onset Intervals)
        lead_events = []
        tick = 0
        while tick < total_section_ticks:
            next_x = 1 - a * (x ** 2) + y
            next_y = b * x
            x, y = next_x, next_y
            
            norm_x = (x + 1.2) / 2.4  # Map typical Henon x range [-1.2, 1.2] to [0.0, 1.0]
            norm_x = np.clip(norm_x, 0.05, 1.0)
            
            grain_duration = int(120 + (norm_x * 480))
            scale_idx = int(norm_x * 6.99)
            pitch = scale_steps[scale_idx] + 12
            
            end_tick = tick + grain_duration
            if end_tick > total_section_ticks:
                end_tick = total_section_ticks
                
            lead_events.append(MusicEvent(pitch=pitch, volume=int(75 + (norm_x * 45)), start_tick=tick, end_tick=end_tick))
            tick += grain_duration
            
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Cloud Pad Generation
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            next_x = 1 - a * (x ** 2) + y
            x, y = next_x, b * x
            norm_x = np.clip((x + 1.2) / 2.4, 0.0, 1.0)
            
            root_idx = int(norm_x * 6.99)
            root = scale_steps[root_idx]
            
            pad_events.append(MusicEvent(pitch=root, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root+3, volume=60, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root+7, volume=60, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Stochastic Bass Generation
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            next_x = 1 - a * (x ** 2) + y
            x, y = next_x, b * x
            norm_x = np.clip((x + 1.2) / 2.4, 0.0, 1.0)
            
            root_idx = int(norm_x * 4)
            root = scale_steps[root_idx] - 12
            
            half_bar = ticks_per_bar // 2
            # Absolute, strict grid boundaries to keep the matrical track alignment perfectly identical
            bass_events.append(MusicEvent(pitch=root, volume=85, start_tick=bar_start, end_tick=bar_start + half_bar))
            bass_events.append(MusicEvent(pitch=root, volume=85, start_tick=bar_start + half_bar, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Chaos Percussion
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            
            # Matrical snare aligned strictly on boundaries
            perc_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + (half_bar // 2), end_tick=bar_start + half_bar))
            perc_events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + (half_bar + (half_bar // 2)), end_tick=bar_start + ticks_per_bar))
            
            # Chaotically triggered Hi-Hats
            for hh_tick in range(0, ticks_per_bar, 240):
                next_x = 1 - a * (x ** 2) + y
                x, y = next_x, b * x
                if x > 0.0:
                    perc_events.append(MusicEvent(pitch=42, volume=70, start_tick=bar_start + hh_tick, end_tick=bar_start + hh_tick + 120))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment validation failed: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/cmcg_chaotic_composition.mid"
    composer.to_midi(midi_path)
    print(f"Matrical MIDI written to => {midi_path}")

if __name__ == "__main__":
    compose_cmcg_32bars()
