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

def compose_portamento_32bars():
    print("=== COMPOSITION 2: METHOD 029 (CONTINUOUS POLYPHONIC PORTAMENTO GLIDE) ===")
    
    # 32 Bars total @ 120 BPM
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=4)
    
    lead_row = composer.add_voice("Glide Lead", program=85, channel=0)       # Charang Synth (sharp slide)
    pad_row = composer.add_voice("Glide Pad", program=90, channel=1)         # Pad Halo (sliding space)
    bass_row = composer.add_voice("Glide Bass", program=38, channel=2)       # Synth Bass (Smooth portamento)
    perc_row = composer.add_voice("Glide Perc", program=0, channel=9)        # Percussion Channel 10
    
    sec_intro = composer.add_section("Intro", bars=8)
    sec_verse = composer.add_section("Verse", bars=8)
    sec_chorus = composer.add_section("Chorus", bars=8)
    sec_outro = composer.add_section("Outro", bars=8)
    
    key_root = 57  # A3
    scale_intervals = [0, 2, 3, 5, 7, 8, 10]
    
    # Chord degrees
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
        print(f"Synthesizing portamento sliding layers for [{sec_name}]...")
        
        # 1. Lead Generation with continuous portamento pitch bend emulation
        lead_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            current_root_deg = degrees[bar % 4]
            next_root_deg = degrees[(bar + 1) % 4]
            
            p1 = get_diatonic_note(key_root, scale_intervals, current_root_deg) + 12
            p2 = get_diatonic_note(key_root, scale_intervals, next_root_deg) + 12
            
            # Divide each bar into small steps to emulate a continuous pitch-sliding curve (Portamento)
            steps = 8
            step_duration = ticks_per_bar // steps
            for s in range(steps):
                # Interpolate the sliding pitch
                fraction = s / steps
                interpolated_pitch = int(p1 + fraction * (p2 - p1))
                
                start = bar_start + (s * step_duration)
                end = start + step_duration
                if end > total_section_ticks:
                    end = total_section_ticks
                    
                lead_events.append(MusicEvent(pitch=interpolated_pitch, volume=80, start_tick=start, end_tick=end))
                
        lead_events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 10, end_tick=total_section_ticks))
        composer.set_unit(lead_row, col_idx, MusicUnit(events=lead_events))
        
        # 2. Sliding Pad
        pad_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            current_root_deg = degrees[bar % 4]
            next_root_deg = degrees[(bar + 1) % 4]
            
            r1 = get_diatonic_note(key_root, scale_intervals, current_root_deg)
            r2 = get_diatonic_note(key_root, scale_intervals, next_root_deg)
            
            steps = 4
            step_duration = ticks_per_bar // steps
            for s in range(steps):
                fraction = s / steps
                current_pitch = int(r1 + fraction * (r2 - r1))
                
                start = bar_start + (s * step_duration)
                end = start + step_duration
                
                pad_events.append(MusicEvent(pitch=current_pitch, volume=65, start_tick=start, end_tick=end))
                pad_events.append(MusicEvent(pitch=current_pitch+4, volume=60, start_tick=start, end_tick=end))
                pad_events.append(MusicEvent(pitch=current_pitch+7, volume=60, start_tick=start, end_tick=end))
        composer.set_unit(pad_row, col_idx, MusicUnit(events=pad_events))
        
        # 3. Sliding Bass
        bass_events = []
        for bar in range(bars_count):
            bar_start = bar * ticks_per_bar
            current_root_deg = degrees[bar % 4]
            next_root_deg = degrees[(bar + 1) % 4]
            
            b1 = get_diatonic_note(key_root, scale_intervals, current_root_deg) - 12
            b2 = get_diatonic_note(key_root, scale_intervals, next_root_deg) - 12
            
            steps = 4
            step_duration = ticks_per_bar // steps
            for s in range(steps):
                fraction = s / steps
                current_pitch = int(b1 + fraction * (b2 - b1))
                
                start = bar_start + (s * step_duration)
                end = start + step_duration
                
                bass_events.append(MusicEvent(pitch=current_pitch, volume=80, start_tick=start, end_tick=end))
        composer.set_unit(bass_row, col_idx, MusicUnit(events=bass_events))
        
        # 4. Standard Backing Percussion
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
    midi_path = "/opt/data/projects/Research/outputs/composition2_portamento.mid"
    composer.to_midi(midi_path)
    print(f"Portamento Composition MIDI exported => {midi_path}")

if __name__ == "__main__":
    compose_portamento_32bars()
