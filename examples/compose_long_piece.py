import sys
import os

# Insert the shared path to make sure musicom is discoverable
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.form_controller import FormPlanController
from structures import MusicUnit, MusicEvent

def create_long_composition():
    print("=== STEP 1: INITIALIZING CORE METRIC MATRIX ===")
    composer = UnitMatrixComposer(bpm=110, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Lead Synth", program=81, channel=0)
    pad_row = composer.add_voice("Harmony Pad", program=89, channel=1)
    bass_row = composer.add_voice("Bass Synth", program=38, channel=2)
    perc_row = composer.add_voice("Drumband Perc", program=0, channel=9)
    
    intro_col = composer.add_section("Intro", bars=4)
    verse1_col = composer.add_section("Verse1", bars=4)
    chorus_col = composer.add_section("Chorus", bars=4)
    outro_col = composer.add_section("Outro", bars=4)
    
    print("=== STEP 2: CALCULATING STRUCTURAL TENSION CURVES ===")
    form_ctrl = FormPlanController(key_center="D", scale_name="minor")
    form_ctrl.add_section("Intro", bars=4, start_tension=0.1, end_tension=0.3)
    form_ctrl.add_section("Verse1", bars=4, start_tension=0.3, end_tension=0.6)
    form_ctrl.add_section("Chorus", bars=4, start_tension=0.7, end_tension=0.9)
    form_ctrl.add_section("Outro", bars=4, start_tension=0.4, end_tension=0.1)
    
    print("=== STEP 3: GENERATING AND ALIGNING MUSICAL MATERIAL ===")
    sections_map = [("Intro", intro_col), ("Verse1", verse1_col), ("Chorus", chorus_col), ("Outro", outro_col)]
    
    chords_map = {
        "Intro": [50, 50, 50, 50],
        "Verse1": [50, 46, 53, 48],
        "Chorus": [50, 46, 48, 45],
        "Outro": [50, 50, 50, 50]
    }
    
    ticks_per_bar = composer.ticks_per_bar
    
    for sec_name, col_idx in sections_map:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        print(f"Generating cell structures for [{sec_name}] across {bars_count} bars ({total_section_ticks} ticks)...")
        
        bounds = form_ctrl.get_generative_bounds(sec_name, bars_count // 2)
        density = bounds["density_rate"]
        
        # 1. Lead Generation
        lead_events = []
        step_ticks = 240 if density > 2.5 else 480
        for tick in range(0, total_section_ticks, step_ticks):
            pitch_offset = 0 if density < 2.0 else (tick // step_ticks) % 3
            lead_pitch = chords_map[sec_name][(tick // ticks_per_bar) % 4] + 12 + pitch_offset
            
            # Clamp the end of the last note to the precise section boundary to prevent drift
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            lead_events.append(MusicEvent(pitch=lead_pitch, volume=90, start_tick=tick, end_tick=end_t))
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Pad Generation
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_pitch = chords_map[sec_name][bar % 4]
            pad_events.append(MusicEvent(pitch=root_pitch, volume=70, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root_pitch+4, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=root_pitch+7, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Bass Generation
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_pitch = chords_map[sec_name][bar % 4] - 12
            # 1920 ticks per bar (4 beats * 480 ticks) split into exactly two halves
            half_bar = ticks_per_bar // 2
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start, end_tick=bar_start + half_bar))
            bass_events.append(MusicEvent(pitch=root_pitch, volume=85, start_tick=bar_start + half_bar, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Percussion
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            # Absolute snare triggers aligned perfectly inside bar boundaries
            perc_events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_start + (half_bar // 2), end_tick=bar_start + half_bar))
            perc_events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_start + (half_bar + (half_bar // 2)), end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== STEP 4: VERIFYING TIME-GRID ALIGNMENT ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"ALIGNMENT ERROR: {err}")
        sys.exit(1)
    print(f"Alignment verification: {err}")
    
    # Ensure research outputs directory exists
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    
    output_midi = "/opt/data/projects/Research/outputs/first_long_composition.mid"
    print(f"=== STEP 5: COMPILING SYMBOLIC MIDI => {output_midi} ===")
    composer.to_midi(output_midi)
    print("MIDI File written successfully!")

if __name__ == "__main__":
    create_long_composition()
