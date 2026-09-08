import numpy as np
import wave
import os

def karplus_strong(freq, duration, sample_rate=44100):
    N = int(sample_rate / freq)
    ring_buf = np.random.uniform(-1, 1, N)
    num_samples = int(duration * sample_rate)
    samples = np.zeros(num_samples)
    for i in range(num_samples):
        samples[i] = ring_buf[0]
        avg = 0.5 * (ring_buf[0] + ring_buf[1]) * 0.996
        ring_buf = np.append(ring_buf[1:], avg)
    return samples

def piano_synthesis(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    s = (0.6 * np.sin(2 * np.pi * freq * t) + 
         0.3 * np.sin(2 * np.pi * 2 * freq * t) + 
         0.1 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.exp(-4 * t)
    return s * env

def save_wav(samples, filename, sample_rate=44100):
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate)
        f.writeframes(samples.tobytes())

if __name__ == "__main__":
    SR = 44100
    # Melody: A4, C5, E5 (A minor triad)
    melody_midis = [69, 72, 76]
    note_dur = 0.5
    
    for instr_name, synth_fn in [("piano", piano_synthesis), ("guitar", karplus_strong)]:
        full_audio = np.array([])
        for midi in melody_midis:
            freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
            note = synth_fn(freq, note_dur, SR)
            full_audio = np.concatenate([full_audio, note])
        
        path = f"projects/002-sound-synthesis/audio/{instr_name}_melody.wav"
        save_wav(full_audio, path, SR)
        print(f"Generated {instr_name} melody.")
