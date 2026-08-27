# Continuous Folk Composer for "Een klein meisje"
# Author: Musicom Agent
# Mode: Continuous Streaming Data Generation

import os
import random
import time
import subprocess
import mido
from mido import Message, MidiFile, MidiTrack

# --- CONFIG ---
PROJECT_DIR = "/opt/data/projects/Styles/Folk/029-een-klein-meisje"
MIDI_PATH = os.path.join(PROJECT_DIR, "MIDI/live_render.mid")
OGG_PATH = os.path.join(PROJECT_DIR, "Audio/live_render.ogg")
MP3_PATH = os.path.join(PROJECT_DIR, "Audio/live_render.mp3")
SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

# D Major Scale (MIDI 62 = D4)
D_MAJOR = [62, 64, 66, 67, 69, 71, 73, 74]

# Patterns
VERSE_DEGREES = [[1, 3, 5, 5], [3, 1, 2, 3]]
CHORUS_DEGREES = [[4, 2, 1, 1], [5, 3, 1, 1]]

CHORDS = {
    'I': [50, 54, 57],   # D
    'IV': [55, 59, 62],  # G
    'V': [57, 61, 64],   # A
}

INSTRUMENTS = {
    0: 0,   # Acoustic Grand Piano (Lead)
    1: 24,  # Nylon Guitar (Chords)
    2: 32,  # Acoustic Bass
}
# Patterns
VERSE_DEGREES = [[1, 3, 5, 5], [3, 1, 2, 3], [5, 4, 3, 2], [1, 5, 1, 1]]
CHORUS_DEGREES = [[4, 6, 5, 4], [5, 7, 1, 1], [4, 2, 1, 3], [5, 5, 1, 1]]

def map_deg(deg, octave=0):
    return D_MAJOR[(deg - 1) % 7] + (12 * octave)

def generate_stream_chunk(num_bars=16):
    """Generates 16 bars of evolving folk music with syncopation."""
    ticks_per_beat = 480
    timelines = {'lead': [], 'chords': [], 'bass': []}
    
    for bar in range(num_bars):
        bar_start = bar * 4 * ticks_per_beat
        is_chorus = (bar // 4) % 2 != 0
        chord_prog = ['IV', 'V', 'I', 'I'] if is_chorus else ['I', 'I', 'V', 'I']
        active_chord = chord_prog[bar % 4]
        chord_pitches = CHORDS[active_chord]
        
        # Lead: Introduce 8th note variations and syncopation
        degs = random.choice(CHORUS_DEGREES if is_chorus else VERSE_DEGREES)
        for i, d in enumerate(degs):
            # 30% chance to split quarter note into two 8th notes (rhythmic variation)
            if random.random() < 0.3:
                # First 8th
                t1 = bar_start + i * ticks_per_beat
                p1 = map_deg(d, octave=1)
                timelines['lead'].append(('on', t1, p1, random.randint(90, 105)))
                timelines['lead'].append(('off', t1 + (ticks_per_beat // 2) - 20, p1, 0))
                
                # Second 8th (stepwise neighbor or repeat)
                t2 = t1 + (ticks_per_beat // 2)
                p2 = map_deg(d + random.choice([-1, 0, 1]), octave=1)
                timelines['lead'].append(('on', t2, p2, random.randint(80, 95)))
                timelines['lead'].append(('off', t2 + (ticks_per_beat // 2) - 20, p2, 0))
            else:
                # Standard Syncopation: 20% chance to anticipation (early onset)
                offset = -120 if random.random() < 0.2 and i > 0 else 0
                t = bar_start + i * ticks_per_beat + offset
                p = map_deg(d, octave=1)
                timelines['lead'].append(('on', t, p, random.randint(85, 110)))
                timelines['lead'].append(('off', t + ticks_per_beat - 40, p, 0))

        # Chords & Bass
        for b in range(4):
            t = bar_start + b * ticks_per_beat
            for idx, p in enumerate(chord_pitches):
                timelines['chords'].append(('on', t + (idx*10), p, random.randint(60, 80)))
                timelines['chords'].append(('off', t + ticks_per_beat - 50, p, 0))
            
            if b % 2 == 0:
                p_bass = chord_pitches[0 if b==0 else 2] - 12
                timelines['bass'].append(('on', t, p_bass, 90))
                timelines['bass'].append(('off', t + (2*ticks_per_beat) - 30, p_bass, 0))
                
    return timelines

def render_and_stream():
    """Generates MIDI, renders HQ OGG, and signals completion."""
    mid = MidiFile()
    meta = MidiTrack()
    mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(108)))
    
    tracks_info = [('lead', 0), ('chords', 1), ('bass', 2)]
    timelines = generate_stream_chunk(32) # 32 bars (~70 seconds)
    
    for name, ch in tracks_info:
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('program_change', program=INSTRUMENTS[ch], channel=ch, time=0))
        
        events = timelines[name]
        events.sort(key=lambda x: x[1])
        curr = 0
        for action, tick, p, v in events:
            delta = tick - curr
            track.append(Message('note_on' if action=='on' else 'note_off', note=p, velocity=v, channel=ch, time=delta))
            curr = tick
            
    mid.save(MIDI_PATH)
    
    # FluidSynth HQ Render
    subprocess.run(["fluidsynth", "-ni", SF2_PATH, MIDI_PATH, "-F", "tmp.wav", "-r", "44100"], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", "tmp.wav", "-af", "loudnorm=I=-14", "-codec:a", "libmp3lame", "-b:a", "192k", MP3_PATH], check=True)
    os.remove("tmp.wav")
    print(f"STREAM_READY: {MP3_PATH}")

if __name__ == "__main__":
    render_and_stream()
