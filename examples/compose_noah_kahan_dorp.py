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

def compose_noah_kahan_dorp_16bars():
    print("=== COMPOSITION: 'HET DORP' NOAH KAHAN FOLK-HARDSTYLE (16 BARS - v5) ===")
    print("Concept: Traditional 'Het Dorp' melody mapped to Noah Kahan Banjo/Guitar fingerpicking, transitioning to Hardstyle drop")
    
    # 16 Bars total @ 140 BPM
    composer = UnitMatrixComposer(bpm=140, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=3) # 3 sections: 6 bars Verse, 2 bars Build, 8 bars Drop
    
    banjo_row = composer.add_voice("Folk Banjo", program=105, channel=0)
    gtr_row = composer.add_voice("Acoustic Guitar", program=24, channel=1)
    bass_row = composer.add_voice("Hardstyle Bass", program=38, channel=2)
    perc_row = composer.add_voice("Hardstyle Perc", program=0, channel=9)
    
    sec_verse = composer.add_section("Folk_Verse", bars=6)
    sec_build = composer.add_section("Snare_Build", bars=2)
    sec_climax = composer.add_section("Climax_Drop", bars=8)
    
    # Key: G Major
    key_root = 55  # G3
    scale_intervals = [0, 2, 4, 5, 7, 9, 11]
    
    # "Het Dorp" Melodious scale degree steps relative to the underlying chords
    # Translates Sonneveld's nostalgic vocal contour:
    # "Thuis heb ik nog een blauwe kist..."
    dorp_melody_degrees = [0, 1, 2, 4, 2, 1, 0, 4, 5, 4, 3, 2, 1]
    
    chords_map = {
        "Folk_Verse": [0, 4, 5, 3],  # G - D - Em - C
        "Snare_Build": [5, 3],       # Em - C
        "Climax_Drop": [0, 4, 5, 3]  # G - D - Em - C
    }
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Folk_Verse", sec_verse), ("Snare_Build", sec_build), ("Climax_Drop", sec_climax)]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = chords_map[sec_name]
        
        # 1. Banjo: Emulates Sonneveld's 'Het Dorp' vocal melody contour using rapid fingerpicked banjo rolls
        banjo_events = []
        tick = 0
        step_ticks = 240  # 8th notes
        
        while tick < total_section_ticks:
            current_bar = tick // ticks_per_bar
            chord_root_deg = degrees[current_bar % len(degrees)]
            
            melody_idx = (tick // step_ticks) % len(dorp_melody_degrees)
            target_deg = chord_root_deg + dorp_melody_degrees[melody_idx]
            
            pitch = get_diatonic_note(key_root, scale_intervals, target_deg) + 12
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            banjo_events.append(MusicEvent(pitch=pitch, volume=90, start_tick=tick, end_tick=end_t))
            tick += step_ticks
            
        banjo_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(banjo_row, col_idx, MusicUnit(events=banjo_events))
        
        # 2. Guitar
        gtr_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % len(degrees)]
            r = get_diatonic_note(key_root, scale_intervals, root_deg)
            t = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            f = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            
            gtr_events.append(MusicEvent(pitch=r, volume=75, start_tick=bar_start, end_tick=bar_start + 480))
            gtr_events.append(MusicEvent(pitch=t, volume=70, start_tick=bar_start, end_tick=bar_start + 480))
            gtr_events.append(MusicEvent(pitch=f, volume=70, start_tick=bar_start + 480, end_tick=bar_start + 960))
            gtr_events.append(MusicEvent(pitch=r, volume=75, start_tick=bar_start + 960, end_tick=bar_start + 1440))
            gtr_events.append(MusicEvent(pitch=t, volume=70, start_tick=bar_start + 1440, end_tick=bar_start + ticks_per_bar))
            gtr_events.append(MusicEvent(pitch=f, volume=70, start_tick=bar_start + 1440, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(gtr_row, col_idx, MusicUnit(events=gtr_events))
        
        # 3. Bass
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % len(degrees)]
            root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
            
            if sec_name == "Climax_Drop":
                for beat in range(4):
                    offbeat_start = bar_start + (beat * 480) + 240
                    bass_events.append(MusicEvent(pitch=root_pitch, volume=95, start_tick=offbeat_start, end_tick=offbeat_start + 240))
            else:
                bass_events.append(MusicEvent(pitch=root_pitch, volume=65, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Percussion
        perc_events = []
        if sec_name == "Folk_Verse":
            for bar in range(bars_count):
                bar_start = bar * ticks_per_bar
                perc_events.append(MusicEvent(pitch=54, volume=50, start_tick=bar_start + 480, end_tick=bar_start + 720))
                perc_events.append(MusicEvent(pitch=54, volume=50, start_tick=bar_start + 1440, end_tick=bar_start + 1680))
        elif sec_name == "Snare_Build":
            perc_events.append(MusicEvent(pitch=38, volume=60, start_tick=0, end_tick=240))
            perc_events.append(MusicEvent(pitch=38, volume=70, start_tick=480, end_tick=720))
            perc_events.append(MusicEvent(pitch=38, volume=75, start_tick=960, end_tick=1080))
            perc_events.append(MusicEvent(pitch=38, volume=75, start_tick=1200, end_tick=1320))
            perc_events.append(MusicEvent(pitch=38, volume=80, start_tick=1440, end_tick=1560))
            perc_events.append(MusicEvent(pitch=38, volume=80, start_tick=1680, end_tick=1800))
            b2_start = ticks_per_bar
            for i, tick_offset in enumerate(range(0, ticks_per_bar, 120)):
                vol = int(75 + (i * 2.1))
                if tick_offset < ticks_per_bar - 240:
                    perc_events.append(MusicEvent(pitch=38, volume=vol, start_tick=b2_start + tick_offset, end_tick=b2_start + tick_offset + 60))
                else:
                    if tick_offset == ticks_per_bar - 240:
                        perc_events.append(MusicEvent(pitch=49, volume=100, start_tick=b2_start + tick_offset, end_tick=b2_start + ticks_per_bar))
        elif sec_name == "Climax_Drop":
            for bar in range(bars_count):
                bar_start = bar * ticks_per_bar
                for beat in range(4):
                    kick_start = bar_start + (beat * 480)
                    perc_events.append(MusicEvent(pitch=36, volume=115, start_tick=kick_start, end_tick=kick_start + 240))
                if bar == 0:
                    perc_events.append(MusicEvent(pitch=49, volume=110, start_tick=bar_start, end_tick=bar_start + 960))
                    
        perc_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(perc_row, col_idx, MusicUnit(events=perc_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment error: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs/v5", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/v5/noah_kahan_dorp_build.mid"
    composer.to_midi(midi_path)
    print(f"MIDI successfully written => {midi_path}")

if __name__ == "__main__":
    compose_noah_kahan_dorp_16bars()
