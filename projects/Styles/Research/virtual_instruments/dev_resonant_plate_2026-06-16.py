import numpy as np
import scipy.signal as signal
import soundfile as sf
import os
import matplotlib.pyplot as plt

def generate_resonant_plate(duration=2.0, fs=44100, freq=440, damping=0.995):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Impulse excitation (pluck/strike)
    excitation = np.zeros_like(t)
    excitation[0:int(0.005 * fs)] = np.random.normal(0, 1, int(0.005 * fs))
    
    # Resonant Plate Model (Approximated by Bank of Bandpass Filters)
    # Ratios for a rectangular plate (non-harmonic)
    modes = [1.0, 1.5, 2.3, 3.4, 4.2]
    amplitudes = [1.0, 0.6, 0.4, 0.3, 0.2]
    
    output = np.zeros_like(t)
    
    for m, amp in zip(modes, amplitudes):
        f_mode = freq * m
        if f_mode > fs / 2:
            continue
            
        # Design second-order resonant filter
        q = 100 * (1.0 / (m**0.5)) # Higher modes decay faster
        b, a = signal.iirpeak(f_mode, q, fs)
        
        # Apply filter to impulse
        mode_sig = signal.lfilter(b, a, excitation)
        
        # Apply exponential decay
        decay = np.exp(-t * (5 / (damping + 0.001)) * m)
        output += mode_sig * decay * amp

    # Normalize
    output = output / np.max(np.abs(output))
    return output

def create_pattern(fs=44100):
    # C4, Eb4, G4, Bb4
    freqs = [261.63, 311.13, 392.00, 466.16]
    total_audio = np.array([])
    
    for f in freqs:
        note = generate_resonant_plate(duration=0.5, fs=fs, freq=f)
        total_audio = np.concatenate([total_audio, note])
        
    return total_audio

if __name__ == "__main__":
    fs = 44100
    audio = create_pattern(fs)
    
    output_dir = "/opt/data/projects/Genres/Research/virtual_instruments/outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    file_base = os.path.join(output_dir, "dev_resonant_plate_2026-06-16")
    sf.write(f"{file_base}.wav", audio, fs)
    
    # Save a simplified representation of MIDI since mido is missing
    with open(f"{file_base}.txt", "w") as f:
        f.write("Pattern: C4, Eb4, G4, Bb4\nDuration: 2s total")
    
    # Generate Plot
    plt.figure(figsize=(10, 4))
    plt.specgram(audio, Fs=fs)
    plt.title("Resonant Plate Spectrogram")
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.savefig(f"{file_base}_graph.png")
    plt.close()

    print(f"Exported to {file_base}")
