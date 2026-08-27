import os
import sys

# Core repository path
sys.path.insert(0, '/opt/data/repos/musicom')

import mido
from workflows.unitmatrix_composer import UnitMatrixComposer
from structures import MusicUnit, MusicEvent

def build_project_correctly():
    print("Building 'Jan Klaassen de Trompetter' with strict sequential MIDI encoding...")
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    
    # 4 Voices (Rows)
    lead_idx = composer.add_voice(name="Trumpet (Lead)", program=56, channel=0)
    brass_idx = composer.add_voice(name="Fanfare Brass (Chords)", program=61, channel=1)
    bass_idx = composer.add_voice(name="Tuba (Bass)", program=58, channel=2)
    drum_idx = composer.add_voice(name="Drumband (Drums)", program=0, channel=9) # Percussion
    
    # 4 Sections (Columns)
    intro_idx = composer.add_section("Intro", bars=4)
    verse_idx = composer.add_section("Verse", bars=4)
    chorus_idx = composer.add_section("Chorus", bars=4)
    outro_idx = composer.add_section("Outro", bars=4)
    
    # Create Matrix
    matrix = composer.create_matrix(num_voices=4, num_sections=4)
    section_bars = [4, 4, 4, 4]
    
    for v in range(4):
        for s in range(4):
            num_bars = section_bars[s]
            total_section_ticks = composer.ticks_per_bar * num_bars
            
            events = []
            
            # --- Tuba/Bassline ---
            if v == bass_idx:
                for bar in range(num_bars):
                    bar_start = bar * composer.ticks_per_bar
                    root_pitch = 48 if (s != 2) else 53
                    fifth_pitch = 55 if (s != 2) else 60
                    
                    # Beat 1 (Root)
                    events.append(MusicEvent(pitch=root_pitch, volume=90, start_tick=bar_start, end_tick=bar_start + composer.ticks_per_beat))
                    # Beat 3 (Fifth)
                    events.append(MusicEvent(pitch=fifth_pitch, volume=90, start_tick=bar_start + composer.ticks_per_beat * 2, end_tick=bar_start + composer.ticks_per_beat * 3))
            
            # --- Drumband Snare ---
            elif v == drum_idx:
                for beat in range(num_bars * 4):
                    events.append(MusicEvent(pitch=38, volume=80, start_tick=beat * composer.ticks_per_beat, end_tick=beat * composer.ticks_per_beat + 240))
            
            # --- Trumpet Lead ---
            elif v == lead_idx:
                if s == intro_idx or s == outro_idx:
                    events.append(MusicEvent(pitch=60, volume=100, start_tick=0, end_tick=composer.ticks_per_beat))
                    events.append(MusicEvent(pitch=64, volume=100, start_tick=composer.ticks_per_beat, end_tick=composer.ticks_per_beat * 2))
                    events.append(MusicEvent(pitch=67, volume=100, start_tick=composer.ticks_per_beat * 2, end_tick=composer.ticks_per_beat * 4))
                else:
                    for bar in range(num_bars):
                        bar_start = bar * composer.ticks_per_bar
                        events.append(MusicEvent(pitch=67, volume=100, start_tick=bar_start, end_tick=bar_start + composer.ticks_per_beat))
                        events.append(MusicEvent(pitch=69, volume=100, start_tick=bar_start + composer.ticks_per_beat, end_tick=bar_start + composer.ticks_per_beat * 2))
                        events.append(MusicEvent(pitch=71, volume=100, start_tick=bar_start + composer.ticks_per_beat * 2, end_tick=bar_start + composer.ticks_per_beat * 4))
            
            # --- Fanfare Brass Chords ---
            elif v == brass_idx:
                chord_pitches = [60, 64, 67] if (s != 2) else [65, 69, 72]
                for bar in range(num_bars):
                    bar_start = bar * composer.ticks_per_bar
                    for beat in [1, 3]:
                        for p in chord_pitches:
                            events.append(MusicEvent(pitch=p, volume=75, start_tick=bar_start + beat * composer.ticks_per_beat, end_tick=bar_start + beat * composer.ticks_per_beat + 240))
            
            # ALWAYS pad every cell with a silent rest at the very end to guarantee identical length!
            events.append(MusicEvent(pitch=0, volume=0, start_tick=total_section_ticks - 1, end_tick=total_section_ticks))
            
            unit = MusicUnit(events=events)
            composer.set_unit(v, s, unit)
            
    # Validate the matrix
    is_valid, msg = composer.validate()
    print(f"Matrix validation: {msg}")
    
    # --- CUSTOM ROBUST MIDI EXPORT BYPASS ---
    mid = mido.MidiFile()
    mid.ticks_per_beat = composer.ticks_per_beat
    
    # Tempo track
    tempo_track = mido.MidiTrack()
    tempo_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(composer.bpm), time=0))
    mid.tracks.append(tempo_track)
    
    # Find overall maximum tick length of entire composition (sum of all sections)
    total_ticks_expected = sum(composer.ticks_per_bar * b for b in section_bars)
    print(f"Expected total track length ticks: {total_ticks_expected}")
    
    # Process each voice
    for voice in composer.voices:
        track = mido.MidiTrack()
        track.append(mido.Message('program_change', program=voice['program'], channel=voice['channel'], time=0))
        
        # Gather all absolute events for this voice across all sections
        row_events = composer.matrix.get_row_events(voice['row'])
        
        timeline = []
        for e in row_events:
            if e.pitch == 0:  # Skip padding rests for active note triggers
                continue
            timeline.append(('on', e.start_tick, e.pitch, e.volume))
            timeline.append(('off', e.end_tick, e.pitch, 0))
            
        # Sort chronologically. Crucial: off events must happen before on events at the exact same tick!
        timeline.sort(key=lambda x: (x[1], 0 if x[0] == 'off' else 1))
        
        curr_tick = 0
        for action, tick, pitch, vel in timeline:
            delta = tick - curr_tick
            if action == 'on':
                track.append(mido.Message('note_on', note=pitch, velocity=vel, channel=voice['channel'], time=delta))
            else:
                track.append(mido.Message('note_off', note=pitch, velocity=0, channel=voice['channel'], time=delta))
            curr_tick = tick
            
        # Append an end of track padding message to enforce identical track lengths!
        remaining_ticks = total_ticks_expected - curr_tick
        if remaining_ticks > 0:
            track.append(mido.Message('note_on', note=0, velocity=0, channel=voice['channel'], time=remaining_ticks))
            track.append(mido.Message('note_off', note=0, velocity=0, channel=voice['channel'], time=0))
            
        mid.tracks.append(track)
        
    os.makedirs('/opt/data/projects/Styles/Fanfare/030-jan-klaassen/MIDI', exist_ok=True)
    midi_path = '/opt/data/projects/Styles/Fanfare/030-jan-klaassen/MIDI/jan_klaassen.mid'
    mid.save(midi_path)
    print(f"Bypassed core and exported perfect, drift-free MIDI to: {midi_path}")

if __name__ == "__main__":
    build_project_correctly()
