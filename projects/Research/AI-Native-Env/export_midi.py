import os
import sys
import json
import random

# Push musicom path for our core UnitMatrix structures
sys.path.insert(0, "/opt/data/repos")

from musicom.structures import (
    MusicUnit,
    MusicEvent,
    MidiInstrument
)
from musicom.workflows import UnitMatrixComposer

# Simple exporter to write standard .mid bytes without using negative-delta mido calls
def export_matrix_to_standard_midi(composer, output_path):
    import mido
    mid = mido.MidiFile()
    mid.ticks_per_beat = composer.ticks_per_beat
    
    # Track 0: Tempo meta
    tempo_track = mido.MidiTrack()
    tempo_track.append(mido.MetaMessage(
        'set_tempo', 
        tempo=mido.bpm2tempo(composer.bpm), 
        time=0
    ))
    mid.tracks.append(tempo_track)
    
    for voice in composer.voices:
        track = mido.MidiTrack()
        # Add program change
        track.append(mido.Message('program_change', program=voice['program'], channel=voice['channel'], time=0))
        
        events = composer.matrix.get_row_events(voice['row'])
        milestones = []
        for e in events:
            if e.pitch == 0 or e.volume == 0:
                continue
            milestones.append((e.start_tick, 'note_on', e.pitch, e.volume))
            milestones.append((e.end_tick, 'note_off', e.pitch, 0))
            
        milestones.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))
        
        last_tick = 0
        for tick, event_type, pitch, vol in milestones:
            delta = int(tick - last_tick)
            if delta < 0:
                delta = 0
                
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
    print(f"[SUCCESS] Exported raw MIDI file: {output_path}")


def orchestrate_and_export_midi():
    print("=== [TIER 1: COGNITIVE ORCHESTRATION] ===")
    
    bpm = 100
    duration_beats = 16  # 4 bars in 4/4
    ticks_per_beat = 480
    total_ticks = duration_beats * ticks_per_beat

    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=ticks_per_beat, beats_per_bar=4)
    composer.create_matrix(num_voices=1, num_sections=1)
    
    # Violin = Program 40
    violin_idx = composer.add_voice('Violin Lead', program=40, channel=0)
    composer.add_section('Folk Melody', bars=4)

    # Folk Scale: D Major Pentatonic
    folk_pitches = [62, 64, 66, 69, 71, 74, 78, 81]
    def get_closest_pitch(raw):
        return min(folk_pitches, key=lambda x: abs(x - raw))

    # Generate notes
    lead_events = []
    curr_tick = 0
    random.seed(101)

    while curr_tick < total_ticks:
        step = random.choice([240, 480, 960])  # 8th, Quarter, or Half
        if curr_tick + step > total_ticks:
            step = total_ticks - curr_tick
            
        raw_pitch = random.randint(62, 81)
        scale_pitch = get_closest_pitch(raw_pitch)
        vol = random.randint(80, 105)

        lead_events.append(MusicEvent(
            pitch=scale_pitch,
            volume=vol,
            start_tick=curr_tick,
            end_tick=curr_tick + step
        ))
        curr_tick += step

    # Load into the UnitMatrix composer
    composer.set_unit(violin_idx, 0, MusicUnit(events=lead_events))

    # ─────────────────────────────────────────────────────────────────────────────
    # OUTPUT NATIVE MIDI FILE
    # ─────────────────────────────────────────────────────────────────────────────
    midi_output_path = "/opt/data/projects/Research/AI-Native-Env/StagedMidi/folk_violin_lead.mid"
    export_matrix_to_standard_midi(composer, midi_output_path)
    
if __name__ == '__main__':
    orchestrate_and_export_midi()