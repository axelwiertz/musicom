# project: 032-bollywood-study
# genre: Bollywood (Cinematic style)
# key: D Bhairavi
# rhythm: Keherwa with syncopated cinematic strings

import sys
import os
import numpy as np
import wave
import itertools

# Paths
sys.path.insert(0, '/root/musicom')
PROJECT_DIR = '/opt/data/projects/032-bollywood-study'
AUDIO_DIR = f"{PROJECT_DIR}/Audio"
MIDI_DIR = f"{PROJECT_DIR}/MIDI"

# --- DNA ---
SCALE = [2, 3, 5, 7, 9, 10, 0] 
CHORDS = [[2, 5, 9], [3, 7, 10], [9, 12, 16], [2, 5, 9]] 
DRUM_PATTERN = [36, 42, 38, 42, 36, 42, 38, 42] 
STRING_STABS = [0, 0, 0, 1, 0, 0, 0, 1]
MELODY_PITCH_PATTERN = [0, 1, 3, 4, 3, 1, 0, -1, 0, 3, 5, 7, 5, 3, 1, 0]

TEMPO = 115 
BEAT = 60.0 / TEMPO
SAMPLE_RATE = 44100

def m2f(m): return 440.0 * (2.0 ** ((m - 69) / 12.0))

def gen_note(mid, dur, amp=0.3, type='sitar'):
    f = m2f(mid)
    n_samples = int(dur * SAMPLE_RATE)
    t = np.linspace(0, dur, n_samples, False)
    if type == 'sitar':
        s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)
    elif type == 'strings':
        vibrato = 1 + 0.005 * np.sin(2 * np.pi * 6 * t)
        s = np.sign(np.sin(2 * np.pi * f * vibrato * t))
    else: # drum
        s = np.sin(2 * np.pi * f * t) * np.exp(-15 * t)
    
    env = np.ones_like(s)
    att = min(int(0.01 * SAMPLE_RATE), n_samples)
    rel = min(int(0.1 * SAMPLE_RATE), n_samples)
    env[:att] = np.linspace(0, 1, att)
    env[-rel:] = np.linspace(1, 0, rel)
    return s * env * amp

def compose():
    total_samples = []
    tick_dur = BEAT / 2
    samples_per_tick = int(tick_dur * SAMPLE_RATE)
    
    for bar in range(16):
        chord = CHORDS[bar % 4]
        for b in range(8): 
            step = np.zeros(samples_per_tick)
            
            # 1. Sitar Melody (quarter notes)
            if b % 2 == 0:
                note_idx = (MELODY_PITCH_PATTERN[(bar * 4 + b // 2) % len(MELODY_PITCH_PATTERN)]) % len(SCALE)
                pitch = SCALE[note_idx] + 60
                mel = gen_note(pitch, tick_dur, amp=0.12, type='sitar')
                step[:len(mel)] += mel
            
            # 2. String Stabs (Syncopated)
            if STRING_STABS[b]:
                for p in chord:
                    stb = gen_note(p + 48, tick_dur, amp=0.06, type='strings')
                    step[:len(stb)] += stb
            
            # 3. Percussion
            drum_pitch = DRUM_PATTERN[b]
            d = gen_note(drum_pitch - 12, tick_dur, amp=0.18, type='drum')
            step[:len(d)] += d
            
            total_samples.extend(step)
            
    return np.array(total_samples)

# Audio
data = compose()
out_path = f"{AUDIO_DIR}/bollywood_movie.wav"
with wave.open(out_path, 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SAMPLE_RATE)
    f.writeframes((np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes())

# MIDI
try:
    from mido import Message, MidiFile, MidiTrack, MetaMessage
    mid = MidiFile()
    mel_t = MidiTrack(); str_t = MidiTrack(); per_t = MidiTrack()
    mid.tracks.extend([mel_t, str_t, per_t])
    mel_t.append(MetaMessage('set_tempo', tempo=int(60000000 / TEMPO)))
    mel_t.append(Message('program_change', program=104, time=0))
    str_t.append(Message('program_change', program=48, time=0))
    per_t.append(Message('program_change', program=116, time=0))
    tpb = 480 // 2
    for bar in range(16):
        chord = CHORDS[bar % 4]
        for b in range(8):
            if b % 2 == 0:
                note_idx = (MELODY_PITCH_PATTERN[(bar * 4 + b // 2) % len(MELODY_PITCH_PATTERN)]) % len(SCALE)
                pitch = SCALE[note_idx] + 60
                mel_t.append(Message('note_on', note=pitch, velocity=105, time=0))
                mel_t.append(Message('note_off', note=pitch, velocity=0, time=tpb))
            else: mel_t.append(Message('note_off', note=0, velocity=0, time=tpb))
            if STRING_STABS[b]:
                for i, p in enumerate(chord): str_t.append(Message('note_on', note=p + 60, velocity=85, time=0))
                str_t.append(Message('note_off', note=chord[0] + 60, velocity=0, time=tpb))
            else: str_t.append(Message('note_off', note=0, velocity=0, time=tpb))
            dp = DRUM_PATTERN[b]
            per_t.append(Message('note_on', note=dp - 12, velocity=115, time=0))
            per_t.append(Message('note_off', note=dp - 12, velocity=0, time=tpb))
    mid.save(f"{MIDI_DIR}/bollywood_movie.mid")
except Exception as e: print(e)
