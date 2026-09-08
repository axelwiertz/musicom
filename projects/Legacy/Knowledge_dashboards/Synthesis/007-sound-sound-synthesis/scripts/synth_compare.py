import numpy as np
import wave
import os

def karplus_strong(freq, duration, sample_rate=44100):
    """
    Simulates a plucked string sound using the Karplus-Strong algorithm.
    """
    N = int(sample_rate / freq)
    # Initialize circular buffer with noise
    ring_buf = np.random.uniform(-1, 1, N)
    
    num_samples = int(duration * sample_rate)
    samples = np.zeros(num_samples)
    
    # Pluck
    for i in range(num_samples):
        samples[i] = ring_buf[0]
        # Average with the next sample to create low-pass filtering effect (decay)
        # Decay factor simulates friction/energy loss
        avg = 0.5 * (ring_buf[0] + ring_buf[1]) * 0.996
        ring_buf = np.append(ring_buf[1:], avg)
        
    return samples

def piano_synthesis(freq, duration, sample_rate=44100):
    """
    Basic additive piano-ish synthesis with exponential decay.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Fundamental + some harmonics
    s = (0.6 * np.sin(2 * np.pi * freq * t) + 
         0.3 * np.sin(2 * np.pi * 2 * freq * t) + 
         0.1 * np.sin(2 * np.pi * 3 * freq * t))
    # Faster initial decay for piano-like percussion
    env = np.exp(-4 * t)
    return s * env

def save_wav(samples, filename, sample_rate=44100):
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(samples.tobytes())

if __name__ == "__main__":
    SR = 44100
    DUR = 2.0
    # A4 = 440Hz
    freq_a4 = 440.0
    
    # Generate Guitar (Karplus-Strong)
    guitar_note = karplus_strong(freq_a4, DUR, SR)
    save_wav(guitar_note, "projects/002-sound-synthesis/audio/guitar_a4.wav", SR)
    
    # Generate Piano
    piano_note = piano_synthesis(freq_a4, DUR, SR)
    save_wav(piano_note, "projects/002-sound-synthesis/audio/piano_a4.wav", SR)
    
    print("Synthesized guitar and piano samples.")
