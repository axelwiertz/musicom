import sys
import os
import json
import random

# Core library path
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from structures import MusicUnit, MusicEvent
from generators.markov_constraint import MarkovConstraintGenerator
from generators.tendency_masking import TendencyMaskingGenerator

def run_project_composition():
    print("=== [TIER 1: COGNITIVE ORCHESTRATION] ===")
    print("Designing 16-bar Traditional Folk Composition: 'De Wind op de Heuvel'")
    
    bpm = 112
    ticks_per_beat = 480
    beats_per_bar = 4
    ticks_per_bar = ticks_per_beat * beats_per_bar
    num_sections = 4
    section_ticks = ticks_per_bar * 4
    
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=ticks_per_beat, beats_per_bar=beats_per_bar)
    composer.create_matrix(num_voices=4, num_sections=num_sections)
    
    lead_violin_idx = composer.add_voice('Violin Lead', program=40, channel=0)
    nylon_guitar_idx = composer.add_voice('Nylon Guitar', program=24, channel=1)
    acoustic_bass_idx = composer.add_voice('Acoustic Bass', program=32, channel=2)
    percussion_idx = composer.add_voice('Frame Drum', program=0, channel=9)
    
    composer.add_section('Intro-Guitar', bars=4)
    composer.add_section('Verse-Entry', bars=4)
    composer.add_section('Chorus-Lift', bars=4)
    composer.add_section('Outro-Decay', bars=4)
    
    d_pentatonic = [38, 40, 42, 45, 47, 50, 52, 54, 57, 59, 62, 64, 66, 69, 71, 74, 76, 78, 81, 83]
    
    print("\n--- [ACTIVE METHOD LOADED] ---")
    print("Method 022: Markov-Constraint Wavefront Sequencing (MCWS)")
    print("Method 023: Tendency Masking Stochastic Bounds")
    print("-----------------------------\n")
    
    mcws = MarkovConstraintGenerator(
        key_pitches=d_pentatonic, 
        default_pitch=62, 
        min_pitch=57, 
        max_pitch=81
    )
    
    tendency_engine = TendencyMaskingGenerator(
        key_pitches=d_pentatonic
    )
    
    random.seed(2026)
    
    for s in range(num_sections):
        # 1. Violin Lead
        if s == 0:
            lead_unit = MusicUnit(events=[MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks)])
        elif s in [1, 3]:
            lead_unit = mcws.generate_voice_section(
                section_ticks=section_ticks, 
                step_ticks=960 if s == 3 else 480, 
                density=0.55 if s == 3 else 0.7,
                volume=80 if s == 3 else 90
            )
        else:
            lead_unit = tendency_engine.generate_voice_section(
                section_ticks=section_ticks,
                step_ticks=240,
                bounds_start=(62, 74),
                bounds_end=(69, 83),
                density=0.8,
                volume=98
            )
            
        # 2. Nylon Guitar Strumming (Baseline Ostinato)
        guitar_events = []
        curr_tick = 0
        while curr_tick < section_ticks:
            step = 480
            bar_idx = curr_tick // ticks_per_bar
            chord = [50, 54, 57] if bar_idx < 2 else ([55, 59, 62] if bar_idx == 2 else [57, 61, 64])
            for p in chord:
                guitar_events.append(MusicEvent(pitch=p, volume=70, start_tick=curr_tick, end_tick=curr_tick + step - 60))
            curr_tick += step
        # Enforce exact section boundary
        if guitar_events[-1].end_tick < section_ticks:
            guitar_events.append(MusicEvent(pitch=0, volume=0, start_tick=guitar_events[-1].end_tick, end_tick=section_ticks))
        guitar_unit = MusicUnit(events=guitar_events)
        
        # 3. Acoustic Bass Root
        bass_events = []
        curr_tick = 0
        while curr_tick < section_ticks:
            step = 960
            bar_idx = curr_tick // ticks_per_bar
            root = 38 if bar_idx < 2 else (43 if bar_idx == 2 else 45)
            if curr_tick % 1920 == 0 or (curr_tick % 1920 == 960 and s > 0):
                bass_events.append(MusicEvent(pitch=root, volume=85, start_tick=curr_tick, end_tick=curr_tick + step - 100))
            curr_tick += step
        # Enforce exact section boundary
        if bass_events and bass_events[-1].end_tick < section_ticks:
            bass_events.append(MusicEvent(pitch=0, volume=0, start_tick=bass_events[-1].end_tick, end_tick=section_ticks))
        elif not bass_events:
            bass_events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks))
        bass_unit = MusicUnit(events=bass_events)
        
        # 4. Frame Drum Heartbeat
        perc_events = []
        curr_tick = 0
        while curr_tick < section_ticks:
            step = 480
            beat = (curr_tick % ticks_per_bar) // ticks_per_beat
            if s > 0:
                if beat == 0:
                    perc_events.append(MusicEvent(pitch=35, volume=90, start_tick=curr_tick, end_tick=curr_tick + 120))
                elif beat == 2:
                    perc_events.append(MusicEvent(pitch=37, volume=75, start_tick=curr_tick, end_tick=curr_tick + 120))
            curr_tick += step
        # Enforce exact section boundary
        if perc_events and perc_events[-1].end_tick < section_ticks:
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=perc_events[-1].end_tick, end_tick=section_ticks))
        elif not perc_events:
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks))
        perc_unit = MusicUnit(events=perc_events)
        
        composer.set_unit(lead_violin_idx, s, lead_unit)
        composer.set_unit(nylon_guitar_idx, s, guitar_unit)
        composer.set_unit(acoustic_bass_idx, s, bass_unit)
        composer.set_unit(percussion_idx, s, perc_unit)

    output_path = "/opt/data/projects/Research/AI-Native-Env/StagedMidi/de_wind_op_de_heuvel.mid"
    composer.to_midi(output_path)
    print(f"\n[SUCCESS] Unified Composition Render Complete -> {output_path}")

if __name__ == '__main__':
    run_project_composition()
