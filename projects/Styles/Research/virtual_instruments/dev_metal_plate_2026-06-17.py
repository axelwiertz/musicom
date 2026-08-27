import numpy as np
import scipy.signal as signal
import soundfile as sf
import datetime
import os

def generate_instrument():
    fs = 44100
    duration = 4.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Target: Resonant Metal Plate (Inharmonic modes)
    # Frequencies for a square plate (clamped) follow ratios like 1, 1.59, 2.13, 2.65, 3.65...
    base_freq = 110.0 # A2
    modes = [1.0, 1.59, 2.13, 2.65, 3.14, 3.65, 4.15, 5.09]
    decays = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    
    audio = np.zeros_like(t)
    
    # Impulse - Strike
    strike_dur = 0.005
    strike = np.random.normal(0, 1, int(fs * strike_dur))
    strike *= np.exp(-np.linspace(0, 5, len(strike)))
    
    # Modal Synthesis
    for m, d in zip(modes, decays):
        f = base_freq * m
        # Resonant filter (Bandpass)
        b, a = signal.iirfilter(2, [f*0.99, f*1.01], rs=60, btype='band', fs=fs)
        # Apply strike to the filter
        mode_sig = signal.lfilter(b, a, np.concatenate([strike, np.zeros(len(t)-len(strike))]))
        # Apply exponential decay
        mode_sig *= np.exp(-t * (5.0 / d))
        audio += mode_sig * d
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # 2-bar melodic pattern (8 notes)
    melody_freqs = [110.0, 138.59, 164.81, 220.0, 207.65, 164.81, 138.59, 110.0] # A major triad ish
    quarter_note = 0.5 # 120 BPM
    full_pattern = np.array([])
    
    for mf in melody_freqs:
        note_audio = np.zeros(int(fs * quarter_note))
        note_t = np.linspace(0, quarter_note, len(note_audio), endpoint=False)
        
        note_strike = np.random.normal(0, 0.5, int(fs * 0.002))
        
        for m, d in zip(modes, decays):
            f = mf * m
            if f > fs/2: continue
            # High Q resonant filter
            q = 500
            bw = f / q
            b, a = signal.iirpeak(f, q, fs=fs)
            sig = signal.lfilter(b, a, np.concatenate([note_strike, np.zeros(len(note_audio)-len(note_strike))]))
            sig *= np.exp(-note_t * (8.0 / d))
            note_audio += sig * d
            
        full_pattern = np.concatenate([full_pattern, note_audio])

    # Normalize pattern
    full_pattern = full_pattern / np.max(np.abs(full_pattern))
    
    path_prefix = "/opt/data/projects/Genres/Research/virtual_instruments/dev_metal_plate_2026-06-17"
    sf.write(f"{path_prefix}.wav", full_pattern, fs)
    # Simulating OGG via soundfile (if supported) or just wav for this env
    sf.write(f"{path_prefix}.ogg", full_pattern, fs)
    
    print(f"Frequencies: {[base_freq * m for m in modes]}")
    print(f"Decays: {decays}")

if __name__ == "__main__":
    generate_instrument()
