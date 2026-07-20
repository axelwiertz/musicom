import sys
import os

# Set up path discovery
sys.path.insert(0, '/opt/data/repos/musicom')

from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.form_controller import FormPlanController
from structures import MusicUnit, MusicEvent

def get_diatonic_note(key_root: int, scale_intervals: list, degree_index: int) -> int:
    octave_shift = degree_index // 7
    scale_step = degree_index % 7
    return key_root + (octave_shift * 12) + scale_intervals[scale_step]

def compose_rules_harmonic_32bars():
    print("=== INITIALIZING HARMONIC RULE-BASED SKELETON COMPOSITION ===")
    
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Rules Lead", program=73, channel=0)
    pad_row = composer.add_voice("Rules Pad", program=48, channel=1)
    bass_row = composer.add_voice("Rules Bass", program=43, channel=2)
    perc_row = composer.add_voice("Rules Perc", program=0, channel=9)
    
    sec_intro = composer.add_section("Intro", bars=8)
    sec_verse = composer.add_section("Verse", bars=8)
    sec_chorus = composer.add_section("Chorus", bars=8)
    sec_outro = composer.add_section("Outro", bars=8)
    
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 8, 10]
    
    progression_blueprint = {
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
        degrees = progression_blueprint[sec_name]
        
        # 1. Pad
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg)
            third_pitch = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            fifth_pitch = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            pad_events.append(MusicEvent(pitch=root_pitch, volume=70, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=third_pitch, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
            pad_events.append(MusicEvent(pitch=fifth_pitch, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 2. Bass
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
        
        # 3. Lead
        lead_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            n1 = get_diatonic_note(key_root, scale_intervals, root_deg) + 12
            n2 = get_diatonic_note(key_root, scale_intervals, root_deg + 1) + 12
            n3 = get_diatonic_note(key_root, scale_intervals, root_deg + 2) + 12
            lead_events.append(MusicEvent(pitch=n1, volume=85, start_tick=bar_start, end_tick=bar_start + 480))
            lead_events.append(MusicEvent(pitch=n2, volume=80, start_tick=bar_start + 480, end_tick=bar_start + 960))
            lead_events.append(MusicEvent(pitch=n3, volume=85, start_tick=bar_start + 960, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 4. Percussion
        perc_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            half_bar = ticks_per_bar // 2
            # Set snare hit on Beat 3 (duration is 240 ticks)
            perc_events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_start + half_bar, end_tick=bar_start + half_bar + 240))
            # Strict boundary pad resting hit on the very final tick of the bar to ensure track timing matches exactly
            perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment validation failed: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/rules_harmonic_composition.mid"
    composer.to_midi(midi_path)
    print(f"Harmonic Rules MIDI written to => {midi_path}")

if __name__ == "__main__":
    compose_rules_harmonic_32bars()
