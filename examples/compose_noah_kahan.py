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

def compose_noah_kahan_hardstyle_16bars():
    print("=== COMPOSITION: NOAH KAHAN FOLK-HARDSTYLE HYBRID (16 BARS - v3) ===")
    print("Core Concept: Melancholic Indie-Folk Banjo & Plucked Guitar (Noah Kahan style) erupting into a Climax Hardstyle Drop")
    
    # 16 Bars total @ 140 BPM (Slightly slower than typical hardstyle, allowing acoustic plucks to breathe)
    composer = UnitMatrixComposer(bpm=140, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=2) # 2 sections, 8 bars each = 16 bars total
    
    banjo_row = composer.add_voice("Acoustic Banjo", program=105, channel=0)  # Acoustic Banjo Lead (Indie Folk)
    gtr_row = composer.add_voice("Acoustic Guitar", program=24, channel=1)   # Nylon Guitar (Steady Fingerpicking)
    bass_row = composer.add_voice("Hardstyle Bass", program=38, channel=2)   # Gated Saw Bass (Offbeats - Climax only)
    kick_row = composer.add_voice("Hardstyle Kick", program=0, channel=9)    # Gated Bass Kick (Channel 10)
    
    sec_intro = composer.add_section("Folk_Verse", bars=8)      # Pure melancholic Noah Kahan acoustic section (Intro)
    sec_climax = composer.add_section("Climax_Drop", bars=8)    # Climax drop erupting with heavy hardstyle pump (Drop)
    
    # Key: G Major (G, A, B, C, D, E, F#) - Noah Kahan's canonical emotional key (warm, nostalgic, bittersweet)
    key_root = 55  # G3
    scale_intervals = [0, 2, 4, 5, 7, 9, 11]
    
    # Chord Degrees: I - V - vi - IV (0 - 4 - 5 - 3) - Bittersweet Indie-Folk Pop Anthem progression (G -> D -> Em -> C)
    chords_map = {
        "Folk_Verse": [0, 4, 5, 3],
        "Climax_Drop": [0, 4, 5, 3]
    }
    
    ticks_per_bar = composer.ticks_per_bar
    sections = [("Folk_Verse", sec_intro), ("Climax_Drop", sec_climax)]
    
    for sec_name, col_idx in sections:
        bars_count = composer.sections[col_idx]["bars"]
        total_section_ticks = ticks_per_bar * bars_count
        degrees = chords_map[sec_name]
        print(f"Synthesizing Hybrid cells for [{sec_name}] over {bars_count} bars...")
        
        # 1. Acoustic Banjo: Rapid, dynamic folk-style arpeggio rolls (Noah Kahan signature)
        banjo_events = []
        tick = 0
        step_ticks = 240  # eighth notes
        
        # Fingerpicking roll pattern: Root -> Third -> Fifth -> Octave -> Fifth -> Third -> Fifth -> Octave
        roll_pattern = [0, 2, 4, 7, 4, 2, 4, 7]
        
        while tick < total_section_ticks:
            current_bar = tick // ticks_per_bar
            chord_root_deg = degrees[current_bar % 4]
            
            note_idx = (tick // step_ticks) % len(roll_pattern)
            target_deg = chord_root_deg + roll_pattern[note_idx]
            
            pitch = get_diatonic_note(key_root, scale_intervals, target_deg) + 12 # high-mid range pluck
            
            end_t = tick + step_ticks
            if end_t > total_section_ticks:
                end_t = total_section_ticks
                
            banjo_events.append(MusicEvent(pitch=pitch, volume=90, start_tick=tick, end_tick=end_t))
            tick += step_ticks
            
        banjo_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(banjo_row, col_idx, MusicUnit(events=banjo_events))
        
        # 2. Acoustic Guitar: Steady continuous fingerpicking chords
        gtr_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            root_deg = degrees[bar % 4]
            r = get_diatonic_note(key_root, scale_intervals, root_deg)
            t = get_diatonic_note(key_root, scale_intervals, root_deg + 2)
            f = get_diatonic_note(key_root, scale_intervals, root_deg + 4)
            
            # Simple alternating picking pattern
            # Beat 1: Root & Third | Beat 2: Fifth | Beat 3: Root | Beat 4: Third & Fifth
            gtr_events.append(MusicEvent(pitch=r, volume=75, start_tick=bar_start, end_tick=bar_start + 480))
            gtr_events.append(MusicEvent(pitch=t, volume=70, start_tick=bar_start, end_tick=bar_start + 480))
            gtr_events.append(MusicEvent(pitch=f, volume=70, start_tick=bar_start + 480, end_tick=bar_start + 960))
            gtr_events.append(MusicEvent(pitch=r, volume=75, start_tick=bar_start + 960, end_tick=bar_start + 1440))
            gtr_events.append(MusicEvent(pitch=t, volume=70, start_tick=bar_start + 1440, end_tick=bar_start + ticks_per_bar))
            gtr_events.append(MusicEvent(pitch=f, volume=70, start_tick=bar_start + 1440, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(gtr_row, col_idx, MusicUnit(events=gtr_events))
        
        # 3. Hardstyle Bass: Active ONLY during the Climax Drop section
        bass_events = []
        if sec_name == "Climax_Drop":
            for bar in range(bars_count):
                bar_start = bar * ticks_per_bar
                root_deg = degrees[bar % 4]
                root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
                
                for beat in range(4):
                    # Classic Hardstyle pumping offbeats on eighth-note "ands"
                    offbeat_start = bar_start + (beat * 480) + 240
                    bass_events.append(MusicEvent(pitch=root_pitch, volume=95, start_tick=offbeat_start, end_tick=offbeat_start + 240))
        else:
            # During Verse, bass plays simple acoustic fundamental root drones to hold the low-end
            for bar in range(bars_count):
                bar_start = bar * ticks_per_bar
                root_deg = degrees[bar % 4]
                root_pitch = get_diatonic_note(key_root, scale_intervals, root_deg) - 12
                bass_events.append(MusicEvent(pitch=root_pitch, volume=60, start_tick=bar_start, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Hardstyle Kick: Heavy gated kicks active ONLY during Climax Climax Drop
        kick_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            
            if sec_name == "Climax_Drop":
                # Heavy gated bass kick on beats 1, 2, 3, 4
                for beat in range(4):
                    kick_start = bar_start + (beat * 480)
                    kick_events.append(MusicEvent(pitch=36, volume=115, start_tick=kick_start, end_tick=kick_start + 240))
            else:
                # During verse, we play a quiet organic folk tambourine pattern (pitch 54) on beats 2 & 4
                kick_events.append(MusicEvent(pitch=54, volume=50, start_tick=bar_start + 480, end_tick=bar_start + 720))
                kick_events.append(MusicEvent(pitch=54, volume=50, start_tick=bar_start + 1440, end_tick=bar_start + 1680))
                
            # strict alignment timing pad
            kick_events.append(MusicEvent(pitch=0, volume=0, start_tick=bar_start + ticks_per_bar - 10, end_tick=bar_start + ticks_per_bar))
        composer.set_unit(kick_row, col_idx, MusicUnit(events=kick_events))
        
    print("=== RUNNING MATRICAL TIME ALIGNMENT CHECK ===")
    is_valid, err = composer.validate()
    if not is_valid:
        print(f"Alignment error: {err}")
        sys.exit(1)
    print(" Matrical alignment: OK")
    
    os.makedirs("/opt/data/projects/Research/outputs/v3", exist_ok=True)
    midi_path = "/opt/data/projects/Research/outputs/v3/noah_kahan_hardstyle_16bars.mid"
    composer.to_midi(midi_path)
    print(f"Noah Kahan Hardstyle MIDI written to => {midi_path}")

if __name__ == "__main__":
    compose_noah_kahan_hardstyle_16bars()
