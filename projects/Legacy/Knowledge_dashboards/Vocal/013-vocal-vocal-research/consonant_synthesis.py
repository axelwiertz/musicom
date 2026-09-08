import numpy as np
import wave
import os

def generate_white_noise(duration, sample_rate=44100):
    return np.random.uniform(-1, 1, int(sample_rate * duration))

def apply_envelope(signal, attack, decay, sample_rate=44100):
    n_samples = len(signal)
    envelope = np.ones(n_samples)
    
    n_attack = int(attack * sample_rate)
    n_decay = int(decay * sample_rate)
    
    if n_attack > 0:
        envelope[:n_attack] = np.linspace(0, 1, n_attack)
    
    if n_decay > 0:
        envelope[-n_decay:] = np.linspace(1, 0, n_decay)
        
    return signal * envelope

def generate_s(duration=0.2, sample_rate=44100):
    """Sibilant 'S' - High-frequency noise"""
    noise = generate_white_noise(duration, sample_rate)
    # Simple high-pass via FFT
    freqs = np.fft.fftfreq(len(noise), 1/sample_rate)
    fft = np.fft.fft(noise)
    fft[np.abs(freqs) < 5000] = 0
    s_sound = np.fft.ifft(fft).real
    return apply_envelope(s_sound, 0.05, 0.05, sample_rate)

def generate_t(sample_rate=44100):
    """Plosive 'T' - Sharp burst"""
    noise = generate_white_noise(0.05, sample_rate)
    freqs = np.fft.fftfreq(len(noise), 1/sample_rate)
    fft = np.fft.fft(noise)
    fft[np.abs(freqs) < 3000] = 0
    t_sound = np.fft.ifft(fft).real
    return apply_envelope(t_sound, 0.005, 0.04, sample_rate)

def generate_p(sample_rate=44100):
    """Plosive 'P' - Low thud + burst"""
    noise = generate_white_noise(0.06, sample_rate)
    # Burst
    freqs = np.fft.fftfreq(len(noise), 1/sample_rate)
    fft = np.fft.fft(noise)
    fft[np.abs(freqs) < 1000] = 0
    p_burst = np.fft.ifft(fft).real
    # Thud
    t = np.linspace(0, 0.06, len(noise))
    thud = np.sin(2 * np.pi * 100 * np.exp(-50 * t)) 
    return apply_envelope(p_burst + 0.5 * thud, 0.005, 0.05, sample_rate)

def save_wav(path, data, sample_rate=44100):
    # Normalize to 16-bit PCM
    data = (data * 32767).astype(np.int16)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(data.tobytes())

if __name__ == "__main__":
    sr = 44100
    s = generate_s()
    t = generate_t()
    p = generate_p()
    
    silence = np.zeros(int(sr * 0.2))
    combined = np.concatenate([s, silence, t, silence, p])
    
    output_path = "/opt/data/projects/013-vocal-research/consonants_test.wav"
    save_wav(output_path, combined, sr)
    print(f"Saved to {output_path}")
