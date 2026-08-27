import numpy as np
import scipy.signal as signal
import soundfile as sf
import matplotlib.pyplot as plt
import os
import struct

# Physical Model: Resonant Metal Plate (Inharmonic Percussion)
# Using Modal Synthesis: Sum of damped sinusoids at inharmonic ratios

def generate_metal_plate_tone(freq, duration, fs=44100):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    ratios = [1.0, 1.59, 2.13, 2.3, 2.65, 3.15, 3.5, 3.65, 4.15, 4.43]
    decays = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1]
    amps = [1.0, 0.6, 0.4, 0.35, 0.25, 0.2, 0.15, 0.1, 0.08, 0.05]
    output = np.zeros_like(t)
    for r, d, a in zip(ratios, decays, amps):
        f_mode = freq * r
        if f_mode > fs / 2: break
        env = np.exp(-t * (5.0 / (d + 0.1))) 
        output += a * env * np.sin(2 * np.pi * f_mode * t)
    noise = np.random.normal(0, 0.1, len(t))
    noise_env = np.exp(-t * 100)
    output += noise * noise_env
    if np.max(np.abs(output)) > 0:
        output /= np.max(np.abs(output))
    return output

def create_midi(path, pitches, beats, bpm=120):
    # Minimal MIDI file creation without external libs
    def delta_time(t):
        if t == 0: return b'\x00'
        res = bytearray()
        while t > 0:
            res.append((t & 0x7f) | 0x80)
            t >>= 7
        res.reverse()
        res[-1] &= 0x7f
        return res

    ticks_per_beat = 480
    track = bytearray()
    last_tick = 0
    
    # Set Tempo
    tempo = int(60000000 / bpm)
    track += b'\x00\xff\x51\x03' + tempo.to_bytes(3, 'big')
    
    events = []
    for pitch, beat in zip(pitches, beats):
        # Convert pitch to MIDI number (A4=440=69)
        midi_note = int(round(12 * np.log2(pitch / 440.0) + 69))
        start_tick = int(beat * ticks_per_beat)
        end_tick = start_tick + 480
        events.append((start_tick, 0x90, midi_note, 100)) # Note on
        events.append((end_tick, 0x80, midi_note, 0))    # Note off
    
    events.sort()
    
    current_tick = 0
    for tick, status, data1, data2 in events:
        dt = tick - current_tick
        track += delta_time(dt)
        track += bytes([status, data1, data2])
        current_tick = tick
        
    track += b'\x00\xff\x2f\x00' # End of track
    
    header = b'MThd' + struct.pack('>IHHH', 6, 0, 1, ticks_per_beat)
    track_header = b'MTrk' + struct.pack('>I', len(track))
    
    with open(path, 'wb') as f:
        f.write(header + track_header + track)

def create_sequence():
    fs = 44100
    bpm = 120
    beat_len = 60 / bpm
    total_len = beat_len * 8
    full_audio = np.zeros(int(fs * total_len))
    pattern_beats = [0, 0.5, 1, 2, 2.5, 3, 4, 4.5, 5, 6, 6.5, 7]
    pitches = [220.0, 261.63, 329.63, 220.0, 392.0, 329.63, 220.0, 261.63, 329.63, 440.0, 392.0, 329.63]
    for beat, freq in zip(pattern_beats, pitches):
        start_idx = int(beat * beat_len * fs)
        tone = generate_metal_plate_tone(freq, 1.5, fs)
        end_idx = min(start_idx + len(tone), len(full_audio))
        full_audio[start_idx:end_idx] += tone[:end_idx-start_idx] * 0.5
    full_audio /= (np.max(np.abs(full_audio)) + 1e-9)
    return full_audio, fs, pitches, pattern_beats

def plot_analysis(path, freq_fund):
    ratios = [1.0, 1.59, 2.13, 2.3, 2.65, 3.15, 3.5, 3.65, 4.15, 4.43]
    freqs = [freq_fund * r for r in ratios]
    plt.figure(figsize=(10, 6))
    plt.stem(freqs, [1.0, 0.6, 0.4, 0.35, 0.25, 0.2, 0.15, 0.1, 0.08, 0.05], basefmt=" ")
    plt.title(f"Resonant Metal Plate Modal Distribution (f0={freq_fund}Hz)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Relative Amplitude")
    plt.grid(True)
    plt.savefig(path)

if __name__ == "__main__":
    audio, samplerate, pitches, beats = create_sequence()
    path_base = "/opt/data/projects/Genres/Research/virtual_instruments/dev_metal_plate_2026-06-18"
    sf.write(f"{path_base}.wav", audio, samplerate)
    sf.write(f"{path_base}.ogg", audio, samplerate)
    create_midi(f"{path_base}.mid", pitches, beats)
    plot_analysis(f"{path_base}_graph.png", 220.0)
