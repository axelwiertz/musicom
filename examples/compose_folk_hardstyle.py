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

def compose_folk_hardstyle_16bars():
    print("=== COMPOSITION: FOLK HARDSTYLE HYBRID (16 BARS) ===")
    print("Core Concept: Driving 150 BPM Hardstyle Kick & Offbeat Bass meets Melodious Diatonic Folk Fiddle")
    
    # 16 Bars total @ 150 BPM (Standard Hardstyle tempo)
    composer = UnitMatrixComposer(bpm=150, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=2) # 2 sections, 8 bars each = 16 bars total
    
    fiddle_row = composer.add_voice("Folk Fiddle", program=110, channel=0)    # Violin/Fiddle Lead
    accord_row = composer.add_voice("Folk Accordion", program=21, channel=1) # Accordion Chords
    bass_row = composer.add_voice("Hardstyle Bass", program=38, channel=2)   # Heavy Saw Bass (Offbeats)
    kick_row = composer.add_voice("Hardstyle Kick", program=0, channel=9)    # Gated Bass Kick (Channel 10)
    
    sec_intro = composer.add_section("Folk_Intro", bars=8)
    sec_climax = composer.add_section("Main_Drop", bars=8)
    
    # Scale: A Dorian (A, B, C, D, E, F#, G) - highly conventional for Balfolk jigs and fiddle tunes
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 9, 10]
    
    # Chord Degrees: i - VII - v - i (0 - 6 - 4 - 0)
    chords_map = {
        "Folk_Intro": [0, 6, 4, 0],
        "Main_Drop": [0, 6, 4, 0]
    }
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Folk_Intro", sec_intro), ("Main_Drop", sec_climax)]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = chords_map[sec_name]
        print(f"Synthesizing Folk Hardstyle cells for [{sec_name}] over {bars_count} bars...")
        
        # 1. Folk Fiddle: Dense, flowing eighth-note jig-style melody (Balfolk Celtic influence)
        fiddle_events = []
        tick = 0
        step_ticks = 240  # eighth notes
        
        # Simple melodic contour vector
        contour = [0, 2, 4, 3, 4, 5, 4, 2]
        
        while tick < total_section_ticks:
            current_bar = tick // ticks_per_bar
            chord_root_deg = degrees[current_bar % 4]
            
            note_idx = (tick // step_ticks) % len(contour)
            target_deg = chord_root_deg + contour[note_idx]
            
            pitch = get_diatonic_note(key_root, scale_intervals, target_deg) + 12 # higher octave lead
            
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            fiddle_events.append(MusicEvent(pitch=pitch, volume=95, start_tick=tick, end_tick=end_t))
            tick += step_ticks
            
        fiddle_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(fiddle_row, col_idx, MusicUnit(events=fiddle_events))
        
        # 2. Accordion Pad: Offbeat pumping skank chords
        accord_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            r = get_diatonic_note(key_root, scale_intervals, root_deg)
            t = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            f = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            
            # Accordion chords hit on offbeat eighth-notes to lock with the pump
            for beat in range(4):
                offbeat_tick = bar_start + (beat * 480) + 240
                accord_events.append(MusicEvent(pitch=r, volume=70, start_tick=offbeat_tick, end_tick=offbeat_tick + 240))
                accord_events.append(MusicEvent(pitch=t, volume=65, start_tick=offbeat_tick, end_tick=offbeat_tick + 240))
                accord_events.append(MusicEvent(pitch=f, volume=65, start_tick=offbeat_tick, end_tick=offbeat_tick + 240))
        composer.set_unit(accord_row, col_idx, MusicUnit(events=accord_events))
        
        # 3. Hardstyle Saw Bass: Heavy driving offbeats (Classic Hardstyle pumping bassline: Root on beats "and")
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
            
            for beat in range(4):
                # Beat "and" (offbeat eighth note)
                offbeat_start = bar_start + (beat * 480) + 240
                bass_events.append(MusicEvent(pitch=root_pitch, volume=90, start_tick=offbeat_start, end_tick=offbeat_start + 240))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Hardstyle Kick: Heavy gated bass kicks on beats 1, 2, 3, 4 (Four-on-the-floor)
        kick_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            for beat in range(4):
                kick_start = bar_start + (beat * 480)
                # Gated kick is simulated using Low Floor Tom on general MIDI (pitch 35 or 36)
                kick_events.append(MusicEvent(pitch=36, volume=115, start_tick=kick_start, end_tick=kick_start + 240))
            # strict alignment timing pad
            kick_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(kick_row, col_idx, MusicUnit(events=kick_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment error: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs/v2", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/v2/folk_hardstyle_16bars.mid"
    composer.to_midi(midi_path)
    print(f"Folk Hardstyle MIDI written to => {midi_path}")

if __name__ == "__main__":
    compose_folk_hardstyle_16bars()
