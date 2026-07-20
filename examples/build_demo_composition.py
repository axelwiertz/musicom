import sys
import os

# Insert shared path
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.form_controller import FormPlanController
from structures import MusicUnit, MusicEvent

def compose_and_build():
    print("=== STEP 1: INITIALIZING 4-TRACK CORE UNITMATRIX ===")
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Lead Synth", program=81, channel=0)      # Saw Lead
    pad_row = composer.add_voice("Harmony Pad", program=89, channel=1)      # Pad Warm
    bass_row = composer.add_voice("Bass Synth", program=38, channel=2)      # Synth Bass 2
    perc_row = composer.add_voice("Drumband Perc", program=0, channel=9)    # Percussion Channel 10
    
    # Define sections
    intro_col = composer.add_section("Intro", bars=4)
    verse1_col = composer.add_section("Verse1", bars=4)
    chorus_col = composer.add_section("Chorus", bars=4)
    outro_col = composer.add_section("Outro", bars=4)
    
    print("=== STEP 2: SCILING PARAMETRIC VALUES VIA FORMPLAN ===")
    form_ctrl = FormPlanController(key_center="A", scale_name="minor")
    form_ctrl.add_section("Intro", bars=4, start_tension=0.1, end_tension=0.3)
    form_ctrl.add_section("Verse1", bars=4, start_tension=0.3, end_tension=0.6)
    form_ctrl.add_section("Chorus", bars=4, start_tension=0.7, end_tension=0.9)
    form_ctrl.add_section("Outro", bars=4, start_tension=0.4, end_tension=0.1)
    
    sections_map = [("Intro", intro_col), ("Verse1", verse1_col), ("Chorus", chorus_col), ("Outro", outro_col)]
    
    # Chord degrees in A Minor: i - bVI - bIII - bVII (Am -> F -> C -> G)
    chords_map = {
        "Intro": [45, 45, 45, 45],
        "Verse1": [45, 41, 48, 43],
        "Chorus": [45, 41, 43, 40],
        "Outro": [45, 45, 45, 45]
    }
    
    ticks_per_bar = composer.ticks_per_bar
    
    for sec_name, col_idx in sections_map:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        print(f"Generating cell structures for [{sec_name}]...")
        
        bounds = form_ctrl.get_generative_bounds(sec_name, bars_count // 2)
        density = bounds["density_rate"]
        
        # 1. Lead Generation
        lead_events = []
        step_ticks = 240 if density > 2.5 else 480
        for tick in range(0, total_section_ticks, step_ticks):
            pitch_offset = 0 if density < 2.0 else (tick // step_ticks) % 3
            lead_pitch = chords_map[sec_name][(tick // ticks_per_bar) % 4] + 12 + pitch_offset
            
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            lead_events.append(MusicEvent(pitch=lead_pitch, volume=95, start_tick=tick, end_tick=end_t))
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Pad Generation
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_pitch = chords_map[sec_name][bar % 4]
            pad_events.append(MusicEvent(pitch=root_pitch, volume=70, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root_pitch+3, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root_pitch+7, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Bass Generation
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_pitch = chords_map[sec_name][bar % 4] - 12
            half_bar = ticks_per_bar // 2
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start, end_tick=bar_start + half_bar))
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start + half_bar, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Percussion
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            perc_events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_start + (half_bar // 2), end_tick=bar_start + half_bar))
            perc_events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_start + (half_bar + (half_bar // 2)), end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== STEP 3: RUNNING GRID ALIGNMENT VERIFICATION ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment validation failed: {err}")
        sys.exit(1)
    print("Grid alignment: PASS")
    
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    output_midi = "/opt/data/projects/Research/outputs/demo_demonstration.mid"
    
    composer.to_midi(output_midi)
    print(f"Midi successfully compiled and exported to => {output_midi}")

if __name__ == "__main__":
    compose_and_build()
