# Algorithmic Folk Composer: "Een klein meisje"
# Tonal Center D (1 = D4, MIDI 62)

import os
import random
import mido
from mido import Message, MidiFile, MidiTrack

# --- SCALES AND STRUCTURES ---
# D Major Scale: D, E, F#, G, A, B, C#
D_MAJOR = [62, 64, 66, 67, 69, 71, 73, 74] # 1 to 8 (Sa equivalent)

# Melodic blocks based on original degrees:
# Verse: 1-3-5-5 | 3-1-2-3 
VERSE_DEGREES = [
    [1, 3, 5, 5],
    [3, 1, 2, 3],
    [1, 3, 5, 5],
    [3, 1, 2, 3]
]

# Melody/Chorus: 4-2-1-1 | 5-3-1-1
CHORUS_DEGREES = [
    [4, 2, 1, 1],
    [5, 3, 1, 1],
    [4, 2, 1, 1],
    [5, 3, 1, 1]
]

# Chords (Roots as MIDI):
CHORDS = {
    'I': [50, 54, 57],   # D Major (Root, 3rd, 5th)
    'IV': [55, 59, 62],  # G Major
    'V': [57, 61, 64],   # A Major
}

INSTRUMENTS = {
    0: 0,   # Acoustic Grand Piano (Vocal voice)
    1: 24,  # Acoustic Guitar (nylon) (Chords)
    2: 32,  # Acoustic Bass (Pizzicato / Picked)
}

def map_degree_to_midi(deg, octave=0):
    val = D_MAJOR[deg - 1]
    return val + (12 * octave)

def generate_folk_section(is_chorus=False):
    """
    Generates 8 measures (4 bars repeated or full form development).
    Returns dict of events per track.
    """
    ticks_per_beat = 480
    events = {'lead': [], 'chords': [], 'bass': []}
    
    degrees = CHORUS_DEGREES if is_chorus else VERSE_DEGREES
    chord_form = ['IV', 'V', 'I', 'I'] if is_chorus else ['I', 'I', 'V', 'I']
    
    # Repeat chord form once to make 8 bars total
    chord_prog = chord_form * 2
    melody_prog = degrees * 2
    
    for bar in range(8):
        bar_start = bar * 4 * ticks_per_beat
        active_chord = chord_prog[bar]
        chord_pitches = CHORDS[active_chord]
        
        # --- LEAD MELODY ---
        mel_degs = melody_prog[bar]
        for note_idx, deg in enumerate(mel_degs):
            start = bar_start + note_idx * ticks_per_beat
            pitch = map_degree_to_midi(deg, octave=1) # High register
            events['lead'].append({
                'pitch': pitch,
                'tick': start,
                'dur': ticks_per_beat - 40,
                'vel': random.randint(90, 110)
            })
            
        # --- CHORDS (Strummed Guitar nylon style) ---
        # Strumming pattern: Onbeat, Syncopated Offbeats (█ ░ █ ░)
        # Strum chord notes on beats 1, 2, 3, 4 with a small roll/arpeggiation delay
        for beat in range(4):
            beat_start = bar_start + beat * ticks_per_beat
            
            # Arpeggiated strum (15ms delay per note)
            for idx, p in enumerate(chord_pitches):
                delay = idx * 10 # small millisecond-equivalent ticks
                events['chords'].append({
                    'pitch': p,
                    'tick': beat_start + delay,
                    'dur': ticks_per_beat - 50,
                    'vel': random.randint(55, 70) if beat > 0 else random.randint(75, 85) # Accent downbeat
                })
                
        # --- BASS (Acoustic pizz walking style) ---
        # Play root note on beat 1, fifth on beat 3
        root_bass = chord_pitches[0] - 12 # Octave lower
        fifth_bass = chord_pitches[2] - 12
        
        events['bass'].append({'pitch': root_bass, 'tick': bar_start, 'dur': ticks_per_beat * 2 - 30, 'vel': 85})
        events['bass'].append({'pitch': fifth_bass, 'tick': bar_start + 2 * ticks_per_beat, 'dur': ticks_per_beat * 2 - 30, 'vel': 75})
        
    return events

def build_folk_midi(num_sections=4, path="/opt/data/projects/Genres/Folk/029-een-kleim-meisje/MIDI/live_render.mid"):
    mid = MidiFile()
    
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(105))) # 105 BPM (Moderate folk)
    
    tracks = {
        'lead': (MidiTrack(), 0),
        'chords': (MidiTrack(), 1),
        'bass': (MidiTrack(), 2)
    }
    
    for ch_name, (track, channel) in tracks.items():
        mid.tracks.append(track)
        track.append(Message('program_change', program=INSTRUMENTS[channel], channel=channel, time=0))
        
    accumulated_tick_offset = {k: 0 for k in tracks.keys()}
    
    # We will build absolute timelines, sort, then delta-encode
    timelines = {'lead': [], 'chords': [], 'bass': []}
    
    ticks_per_bar = 4 * 480
    ticks_per_sec = 8 * ticks_per_bar
    
    for sec in range(num_sections):
        sec_start = sec * ticks_per_sec
        # Alternating verse and chorus
        is_ch = (sec % 2 != 0) 
        sec_events = generate_folk_section(is_chorus=is_ch)
        
        for name in timelines.keys():
            for ev in sec_events[name]:
                abs_on = sec_start + ev['tick']
                abs_off = abs_on + ev['dur']
                timelines[name].append(('on', abs_on, ev['pitch'], ev['vel']))
                timelines[name].append(('off', abs_off, ev['pitch'], 0))
                
    # Delta-write each timeline to tracks
    for name, (track, channel) in tracks.items():
        timeline = timelines[name]
        timeline.sort(key=lambda x: (x[1], 0 if x[0] == 'off' else 1))
        curr_time = 0
        for action, tick, pitch, vel in timeline:
            delta = tick - curr_time
            if delta < 0:
                delta = 0
            if action == 'on':
                track.append(Message('note_on', note=pitch, velocity=vel, channel=channel, time=delta))
            else:
                track.append(Message('note_off', note=pitch, velocity=0, channel=channel, time=delta))
            curr_time = tick
            
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mid.save(path)
    print(f"Folk MIDI generated successfully at: {path}")

if __name__ == "__main__":
    dst_path = "/opt/data/projects/Genres/Folk/029-een-klein-meisje/MIDI/live_render.mid"
    build_folk_midi(num_sections=4, path=dst_path)
