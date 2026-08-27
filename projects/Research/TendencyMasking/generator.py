import sys
import os
import random
import numpy as np

# Push musicom path
sys.path.insert(0, "/opt/data/repos")

from musicom.structures import (
    MusicUnit, 
    MusicEvent, 
    TimeConverter, 
    MidiInstrument,
    UnitMatrix
)
from musicom.workflows import UnitMatrixComposer

# Create custom mido-friendly exporter inside this file to bypass bug
def save_unit_matrix_to_midi(composer, output_path):
    import mido
    mid = mido.MidiFile()
    mid.ticks_per_beat = composer.ticks_per_beat
    
    # Add tempo track
    tempo_track = mido.MidiTrack()
    tempo_track.append(mido.MetaMessage(
        'set_tempo', 
        tempo=mido.bpm2tempo(composer.bpm), 
        time=0
    ))
    mid.tracks.append(tempo_track)
    
    # Custom absolute tick-to-delta logic to output perfect MIDI events without negative deltas
    for voice in composer.voices:
        track = mido.MidiTrack()
        
        # Add program change
        track.append(mido.Message('program_change', program=voice['program'], channel=voice['channel'], time=0))
        
        # Get all aligned absolute events
        events = composer.matrix.get_row_events(voice['row'])
        
        # Flatten into list of (tick, type, pitch, volume)
        milestones = []
        for e in events:
            if e.pitch == 0 or e.volume == 0:
                continue # Skip rests
            milestones.append((e.start_tick, 'note_on', e.pitch, e.volume))
            milestones.append((e.end_tick, 'note_off', e.pitch, 0))
            
        # Sort chronologically, prioritizing note_off if at same tick
        milestones.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))
        
        last_tick = 0
        for tick, event_type, pitch, vol in milestones:
            delta = int(tick - last_tick)
            if delta < 0:
                delta = 0 # Safety guard
                
            track.append(mido.Message(
                event_type,
                note=int(pitch),
                velocity=int(vol if event_type == 'note_on' else 0),
                channel=voice['channel'],
                time=delta
            ))
            last_tick = tick
            
        mid.tracks.append(track)
        
    mid.save(output_path)
    print(f"[SUCCESS] Saved clean MIDI to {output_path}")


def generate_tendency_mask_composition():
    composer = UnitMatrixComposer(bpm=110, ticks_per_beat=480, beats_per_bar=4)
    ticks_per_bar = 1920
    section_bars = 4
    section_ticks = ticks_per_bar * section_bars
    num_sections = 4
    num_voices = 3
    
    composer.create_matrix(num_voices=num_voices, num_sections=num_sections)
    
    lead_idx = composer.add_voice('Lead Cloud', program=40, channel=0)
    pad_idx = composer.add_voice('Spectral Pad', program=89, channel=1)
    bass_idx = composer.add_voice('Sub Bass', program=38, channel=2)
    
    composer.add_section('Intro-Sparse', bars=section_bars)
    composer.add_section('Expansion', bars=section_bars)
    composer.add_section('Peak-Chaos', bars=section_bars)
    composer.add_section('Contraction', bars=section_bars)
    
    random.seed(42)
    np.random.seed(42)
    
    scale_pitches = [31, 34, 36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86, 89]
    
    def get_closest_in_scale(pitch):
        return min(scale_pitches, key=lambda x: abs(x - pitch))

    def get_mask_bounds(voice, t):
        if voice == 'lead':
            if t < 0.25:
                u = 74 - (4 * t)
                l = 70 - (10 * t)
                density = 1.0 + (2.0 * t)
            elif t < 0.50:
                u = 73 + 40 * (t - 0.25)
                l = 67 - 40 * (t - 0.25)
                density = 1.5 + 6.0 * (t - 0.25)
            elif t < 0.75:
                u = 83 - 20 * (t - 0.50)
                l = 57 + 20 * (t - 0.50)
                density = 3.0 + 8.0 * (0.25 - (t - 0.50))
            else:
                u = 78 - 32 * (t - 0.75)
                l = 62 + 20 * (t - 0.75)
                density = 2.0 - 4.0 * (t - 0.75)
            return int(l), int(u), max(0.5, density)
            
        elif voice == 'pad':
            return 46, 67, 0.5
            
        elif voice == 'bass':
            l = 31
            u = 38 + 12 * t if t < 0.75 else 31 + 7 * (1.0 - t)
            density = 0.25 + 0.5 * t
            return int(l), int(u), density

    for sec_col in range(num_sections):
        section_start_t = sec_col * 0.25
        
        # ── LEAD SYNTH ──
        lead_events = []
        curr_tick = 0
        while curr_tick < section_ticks:
            local_t = section_start_t + (curr_tick / section_ticks) * 0.25
            l_bound, u_bound, density = get_mask_bounds('lead', local_t)
            
            avg_step = 480 / density
            step = int(np.random.exponential(avg_step))
            step = max(120, min(1920, (step // 120) * 120))
            
            if curr_tick + step > section_ticks:
                step = section_ticks - curr_tick
                
            raw_pitch = random.randint(l_bound, u_bound)
            scale_pitch = get_closest_in_scale(raw_pitch)
            
            vol = int(50 + 40 * (raw_pitch - l_bound) / (max(1, u_bound - l_bound)))
            vol = max(40, min(110, vol))
            
            lead_events.append(MusicEvent(
                pitch=scale_pitch,
                volume=vol,
                start_tick=curr_tick,
                end_tick=curr_tick + step
            ))
            curr_tick += step
        
        # ── PAD ──
        pad_events = []
        curr_tick = 0
        chord_dur = 1920
        while curr_tick < section_ticks:
            local_t = section_start_t + (curr_tick / section_ticks) * 0.25
            l_bound, u_bound, _ = get_mask_bounds('pad', local_t)
            
            pitches_in_bounds = [p for p in scale_pitches if l_bound <= p <= u_bound]
            if len(pitches_in_bounds) >= 3:
                chord = random.sample(pitches_in_bounds, 3)
            elif len(pitches_in_bounds) > 0:
                chord = pitches_in_bounds * 3
            else:
                chord = [48, 55, 62]
                
            for p in chord:
                pad_events.append(MusicEvent(
                    pitch=p,
                    volume=65,
                    start_tick=curr_tick,
                    end_tick=curr_tick + chord_dur
                ))
            curr_tick += chord_dur

        # ── BASS ──
        bass_events = []
        curr_tick = 0
        while curr_tick < section_ticks:
            local_t = section_start_t + (curr_tick / section_ticks) * 0.25
            l_bound, u_bound, density = get_mask_bounds('bass', local_t)
            
            avg_step = 480 / density
            step = int(np.random.exponential(avg_step))
            step = max(480, min(3840, (step // 480) * 480))
            
            if curr_tick + step > section_ticks:
                step = section_ticks - curr_tick
                
            raw_pitch = random.randint(l_bound, u_bound)
            scale_pitch = get_closest_in_scale(raw_pitch)
            
            bass_events.append(MusicEvent(
                pitch=scale_pitch,
                volume=85 if random.random() < 0.8 else 0,
                start_tick=curr_tick,
                end_tick=curr_tick + step
            ))
            curr_tick += step

        # Place units
        composer.set_unit(lead_idx, sec_col, MusicUnit(events=lead_events))
        composer.set_unit(pad_idx, sec_col, MusicUnit(events=pad_events))
        composer.set_unit(bass_idx, sec_col, MusicUnit(events=bass_events))

    output_mid = "/opt/data/projects/Research/TendencyMasking/tendency_mask_stochastic.mid"
    save_unit_matrix_to_midi(composer, output_mid)
    
    # ── VISUALIZE RHYTHMIC GRAVITY / DENSITY ──
    print("\n[RHYTHMIC DENSITY VISUAL - LEAD SYNTH]")
    for s in range(num_sections):
        unit = composer.matrix.get_unit((lead_idx, s))
        steps = ["░"] * 16
        for ev in unit.events:
            start_q = ev.start_tick // 480
            end_q = ev.end_tick // 480
            for step_idx in range(start_q, min(16, end_q)):
                steps[step_idx] = "█"
        visual = "".join(steps)
        print(f"Sec {s+1} ({composer.sections[s]['name']}): {visual}")

if __name__ == '__main__':
    generate_tendency_mask_composition()