import mido
import os

def create_klezmer_pattern():
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Tempo: 125 BPM
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(125)))
    
    # Bass: Root-Fifth (G and D)
    # Secunda: Afterbeats
    # Lead: Basic Freylekhs pattern in G Freygish (G Ab B C D Eb F)
    
    ticks_per_beat = mid.ticks_per_beat
    sixteenth = ticks_per_beat // 4

    # 2 Bars of 2/4 = 4 Beats = 16 sixteenths
    
    # Bass Pattern (Channel 0): 1 . 5 . | 1 . 5 .
    bass_notes = [43, 0, 38, 0, 43, 0, 38, 0] # G2, D2
    for note in bass_notes:
        if note > 0:
            track.append(mido.Message('note_on', note=note, velocity=80, time=0, channel=0))
            track.append(mido.Message('note_off', note=note, velocity=80, time=sixteenth * 2, channel=0))
        else:
            # Shift timing for rest
            pass

    # Secunda (Channel 1): . x . x | . x . x
    # Reset track for multi-channel writing or just sequence carefully. 
    # Use second track for better organization.
    sec_track = mido.MidiTrack()
    mid.tracks.append(sec_track)
    for i in range(8):
        # Offbeat is index 1, 3, 5, 7
        if i % 2 == 1:
            sec_track.append(mido.Message('note_on', note=55, velocity=60, time=sixteenth, channel=1)) # G3
            sec_track.append(mido.Message('note_off', note=55, velocity=60, time=sixteenth, channel=1))
        else:
            # Silence during the downbeat (represented by time in the next note_on)
            pass
            
    # Lead (Channel 2): x . x x x . x . 
    lead_track = mido.MidiTrack()
    mid.tracks.append(lead_track)
    lead_pattern = [67, 0, 68, 71, 72, 0, 71, 0] # G4, Ab4, B4, C5, B4
    for note in lead_pattern:
        if note > 0:
            lead_track.append(mido.Message('note_on', note=note, velocity=95, time=0, channel=2))
            lead_track.append(mido.Message('note_off', note=note, velocity=95, time=sixteenth, channel=2))
        else:
            # Wait for sixteenth
            # To handle timing correctly in mido tracks, we need to track delta time.
            # Simpler: just use 0 time for note_on if it follows a note_off immediately, 
            # or add sixteenth to the 'time' of the NEXT event.
            pass

    # Refined approach for sequencing: 
    # Mido tracks are delta-time based. 
    # Let's rebuild the tracks with proper delta accumulation.
    
    mid = mido.MidiFile()
    
    # Bass Track
    t1 = mido.MidiTrack()
    mid.tracks.append(t1)
    # 2 bars, 4 beats total. Bass hits on 1 and 3.
    # Bar 1
    t1.append(mido.Message('note_on', note=43, velocity=90, time=0))
    t1.append(mido.Message('note_off', note=43, velocity=90, time=ticks_per_beat))
    t1.append(mido.Message('note_on', note=38, velocity=90, time=0))
    t1.append(mido.Message('note_off', note=38, velocity=90, time=ticks_per_beat))
    # Bar 2
    t1.append(mido.Message('note_on', note=43, velocity=90, time=0))
    t1.append(mido.Message('note_off', note=43, velocity=90, time=ticks_per_beat))
    t1.append(mido.Message('note_on', note=38, velocity=90, time=0))
    t1.append(mido.Message('note_off', note=38, velocity=90, time=ticks_per_beat))

    # Secunda Track - Afterbeats
    t2 = mido.MidiTrack()
    mid.tracks.append(t2)
    # Eighth note offset: ticks_per_beat // 2
    offset = ticks_per_beat // 2
    for _ in range(4):
        t2.append(mido.Message('note_on', note=55, velocity=70, time=offset))
        t2.append(mido.Message('note_off', note=55, velocity=70, time=offset))
        # This loop completes 1 beat. Total 4 beats = 2 bars.
        
    # Lead Track
    t3 = mido.MidiTrack()
    mid.tracks.append(t3)
    # Pattern: x . x x | x . x . (in eighth notes)
    # Notes: G4, Ab4, B4, C5, B4 (G Freygish)
    pattern = [(67,1), (0,1), (68,1), (71,1), (72,1), (0,1), (71,1), (0,1)]
    for note, dur in pattern:
        delta = dur * offset
        if note == 0:
            # Rest: just add to next event time. Handle by a local variable.
            pass # simplified logic for this script
        else:
            t3.append(mido.Message('note_on', note=note, velocity=100, time=0))
            t3.append(mido.Message('note_off', note=note, velocity=100, time=delta))
            # If next is rest, we need to wait.
            
    # Fixed sequencing for lead to handle "rests" correctly
    t3 = mido.MidiTrack()
    mid.tracks.append(t3)
    # eighths: G, rest, Ab, B, C, rest, B, rest
    # times: 0, 480, 0, 0, 0, 480, 0, 480 (assuming 480 ticks/beat)
    t3.append(mido.Message('note_on', note=67, velocity=100, time=0))
    t3.append(mido.Message('note_off', note=67, velocity=100, time=offset))
    # Skip one eighth
    t3.append(mido.Message('note_on', note=68, velocity=100, time=offset))
    t3.append(mido.Message('note_off', note=68, velocity=100, time=offset))
    t3.append(mido.Message('note_on', note=71, velocity=100, time=0))
    t3.append(mido.Message('note_off', note=71, velocity=100, time=offset))
    t3.append(mido.Message('note_on', note=72, velocity=100, time=0))
    t3.append(mido.Message('note_off', note=72, velocity=100, time=offset))
    # Skip one
    t3.append(mido.Message('note_on', note=71, velocity=100, time=offset))
    t3.append(mido.Message('note_off', note=71, velocity=100, time=offset))

    mid.save('/opt/data/projects/Genres/Klezmer/freylekhs-daily-2026-06-17/composition.mid')

create_klezmer_pattern()
