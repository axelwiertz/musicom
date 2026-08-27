# Algorithmic Infinite Gamelan Composer
# Centered in D Slendro with Colotomic structural weights

import os
import random
import mido
from mido import Message, MidiFile, MidiTrack

# --- SCALES AND CONSTANTS ---
# D Slendro pitch mappings:
# Note name to MIDI: D4 (62), E4 (64), F#4 (66), A4 (69), B4 (71)
SLENDRO_PITCHES = [62, 64, 66, 69, 71, 74] # Octave wrap included for movement
TONIC_BASS = 38 # D3 for Kenong
GONG_PITCH = 26 # D2 for Gong Ageng
KEMPUL_PITCH = 45 # A3
KETHUK_PITCH = 50 # D4 / wood block or damp pot sound

# Percussion/Instrument Channel allocations in GM:
# Channel 0: Saron (Balungan core) -> Track 1 (e.g., GM Tubular Bells or Marimba 12/14)
# Channel 1: Peking (Elaborated) -> Track 2 (GM Glockenspiel / Vibraphone 9/11)
# Channel 2: Colotomic Pots (Kenong, Kempul, Kethuk) -> Track 3 (Woodblock / Timpani / Synth Mallet)
# Channel 3: Gong Ageng -> Track 4 (Low deep synth / church bell 14)

INSTRUMENTS = {
    0: 12, # Marimba (Saron core)
    1: 9,  # Glockenspiel (Peking)
    2: 12, # Marimba lower (Muffled Pots / Kempul / Kenong)
    3: 14, # Tubular Bells (Gong Ageng)
}

def generate_gamelan_cycle(prev_note=62):
    """
    Generates single 16-beat cycle of Gamelan music.
    Returns:
       dict of tracks with tick events
    """
    ticks_per_beat = 480
    cycle_beats = 16
    
    # 1. Generate Balungan (1 beat duration each)
    # Markov chain transition for stepwise Slendro walk
    balungan_pattern = []
    curr = prev_note
    if curr not in SLENDRO_PITCHES:
        curr = 62
        
    for beat in range(cycle_beats):
        idx = SLENDRO_PITCHES.index(curr)
        # Choose neighbor step [-1, 0, 1]
        step = random.choice([-1, 0, 1, -2, 2]) if beat > 0 else 0
        new_idx = max(0, min(len(SLENDRO_PITCHES) - 1, idx + step))
        curr = SLENDRO_PITCHES[new_idx]
        balungan_pattern.append(curr)
        
    # Colotomic grid definitions:
    # Beat indices (0-15):
    # Gong: 15
    # Kenong: 3, 7, 11, 15
    # Kempul: 5, 9, 13
    # Kethuk: 0, 2, 4, 6, 8, 10, 12, 14 (all odd beats)
    
    events = {
        'saron': [],   # Ch 0
        'peking': [],  # Ch 1
        'pots': [],    # Ch 2 (Kethuk, Kempul, Kenong)
        'gong': []     # Ch 3
    }
    
    for beat in range(cycle_beats):
        start_tick = beat * ticks_per_beat
        dur_tick = ticks_per_beat
        
        # --- SARON (Balungan) ---
        pitch = balungan_pattern[beat]
        events['saron'].append({'pitch': pitch, 'tick': start_tick, 'dur': dur_tick - 20, 'vel': 90})
        
        # --- PEKING (Elaboration - plays double speed, anticipation) ---
        # Plays twice per beat
        sub_dur = ticks_per_beat // 2
        # Anticipation logic: subbeat 1 plays active Balungan note, subbeat 2 plays target of NEXT beat
        p1 = pitch
        next_beat_idx = (beat + 1) % cycle_beats
        p2 = balungan_pattern[next_beat_idx]
        
        events['peking'].append({'pitch': p1, 'tick': start_tick, 'dur': sub_dur - 10, 'vel': 85})
        events['peking'].append({'pitch': p2, 'tick': start_tick + sub_dur, 'dur': sub_dur - 10, 'vel': 100})
        
        # --- COLOTOMIC POTS ---
        # Kethuk (Offbeats)
        if beat in [0, 2, 4, 6, 8, 10, 12, 14]:
            events['pots'].append({'pitch': KETHUK_PITCH, 'tick': start_tick, 'dur': 120, 'vel': 75})
            
        # Kempul (Punctuation)
        if beat in [5, 9, 13]:
            events['pots'].append({'pitch': KEMPUL_PITCH, 'tick': start_tick, 'dur': ticks_per_beat, 'vel': 85})
            
        # Kenong (Phrase ends)
        if beat in [3, 7, 11, 15]:
            # Alternate octave for structure
            pitch_kenong = TONIC_BASS if beat < 15 else TONIC_BASS + 12
            events['pots'].append({'pitch': pitch_kenong, 'tick': start_tick, 'dur': ticks_per_beat, 'vel': 95})
            
        # --- GONG AGENG (Heavy final accent on beat 16) ---
        if beat == 15:
            events['gong'].append({'pitch': GONG_PITCH, 'tick': start_tick, 'dur': ticks_per_beat * 2, 'vel': 120})
            
    return events, balungan_pattern

def build_midi_score(num_cycles=4, path="/opt/data/projects/Genres/Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid"):
    mid = MidiFile()
    
    # Create program change track
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(80))) # 80 BPM - Irama I
    
    # Initialize Tracks
    tracks = {
        'saron': (MidiTrack(), 0),
        'peking': (MidiTrack(), 1),
        'pots': (MidiTrack(), 2),
        'gong': (MidiTrack(), 3)
    }
    
    for ch_name, (track, channel) in tracks.items():
        mid.tracks.append(track)
        # Assign instruments
        track.append(Message('program_change', program=INSTRUMENTS[channel], channel=channel, time=0))
        
    last_note = 62
    accumulated_tick_offset = {k: 0 for k in tracks.keys()}
    
    all_balungans = []
    
    for cycle in range(num_cycles):
        cycle_events, bal_path = generate_gamelan_cycle(last_note)
        last_note = bal_path[-1]
        all_balungans.append(bal_path)
        
        ticks_per_cycle = 16 * 480
        cycle_start_tick = cycle * ticks_per_cycle
        
        for name, (track, channel) in tracks.items():
            events = sorted(cycle_events[name], key=lambda x: x['tick'])
            
            # Format to delta-time messages for MIDI track
            curr_pos = cycle_start_tick
            for ev in events:
                abs_on = ev['tick'] + cycle_start_tick
                abs_off = abs_on + ev['dur']
                
                # Delta note_on
                delta_on = abs_on - accumulated_tick_offset[name]
                track.append(Message('note_on', note=ev['pitch'], velocity=ev['vel'], channel=channel, time=delta_on))
                accumulated_tick_offset[name] = abs_on
                
                # Delta note_off
                delta_off = abs_off - accumulated_tick_offset[name]
                track.append(Message('note_off', note=ev['pitch'], velocity=0, channel=channel, time=delta_off))
                accumulated_tick_offset[name] = abs_off

    # Finalize tracks
    for name, (track, channel) in tracks.items():
        # Ensure tracks align cleanly at end
        final_delta = (num_cycles * 16 * 480) - accumulated_tick_offset[name]
        if final_delta > 0:
            track.append(Message('note_off', note=0, velocity=0, channel=channel, time=final_delta))

    # Save
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mid.save(path)
    return all_balungans

if __name__ == "__main__":
    print("Generating 8 sequential cycles of live-mutated Gamelan ...")
    balungans = build_midi_score(num_cycles=8)
    print("Done! MIDI generated successfully.")
    
    # Show active ASCII representation of mutated Balungans
    # Slendro notes mapping: D (62) -> 1, E (64) -> 2, F# (66) -> 3, A (69) -> 5, B (71) -> 6, D (74) -> i
    pitch_map = {62: '1', 64: '2', 66: '3', 69: '5', 71: '6', 74: 'i'}
    print("\nVisualizing Mutating Balungan Walk:\n")
    for idx, path in enumerate(balungans):
        glyphs = "".join([pitch_map[p] + " " for p in path])
        # Grid line representation
        grid = "".join(["█" if p != 62 else "░" for p in path])
        print(f"Cycle {idx+1:02d} [{pitch_map[path[0]]}->{pitch_map[path[-1]]}]: {glyphs} | {grid}")
