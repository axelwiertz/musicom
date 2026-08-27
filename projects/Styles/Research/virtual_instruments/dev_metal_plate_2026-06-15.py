import numpy as np
import scipy.signal as signal
import soundfile as sf
from datetime import datetime
import os

def create_resonant_metal_plate():
    fs = 44100
    duration = 4.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Target: Resonant Metal Plate (Inharmonic Percussion)
    # 1. Excitation: Short burst of noise + sharp impulse
    excitation = np.random.normal(0, 0.1, len(t))
    env_exc = np.exp(-1000 * t)
    excitation *= env_exc
    
    # 2. Resonators: Inharmonic modes for metal plate
    # Typical plate ratios: 1.0, 1.5, 2.5, 3.5, 4.6...
    base_f = 120.0
    modes = [1.0, 1.73, 2.45, 2.72, 3.14, 4.02, 5.11, 7.23]
    qs = [500, 400, 300, 250, 200, 150, 100, 80]
    
    output = np.zeros_like(t)
    
    params = []
    for f_ratio, q in zip(modes, qs):
        freq = base_f * f_ratio
        if freq > fs / 2:
            continue
        
        # Design resonant bandpass
        b, a = signal.iirpeak(freq, q, fs)
        mode_sig = signal.lfilter(b, a, excitation)
        
        # Gain compensation
        mode_sig *= (1.0 / np.max(np.abs(mode_sig)) if np.max(np.abs(mode_sig)) > 0 else 0)
        mode_sig *= np.exp(-1.5 * f_ratio * t) # Higher modes decay faster
        
        output += mode_sig
        params.append({"f": freq, "q": q})

    # Normalize
    output /= np.max(np.abs(output))
    
    return t, output, params

def generate_melodic_study(t, single_hit, fs=44100):
    # 2-bar pattern at 120 BPM (4 seconds)
    # Simple rhythmic pattern
    pattern = [0, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5, 3.0]
    total_len = int(fs * 4.5)
    full_audio = np.zeros(total_len)
    
    for start_time in pattern:
        start_idx = int(start_time * fs)
        length = min(len(single_hit), total_len - start_idx)
        # Pitch shifting would be better with resample, keeping it simple
        full_audio[start_idx : start_idx + length] += single_hit[:length] * 0.8
        
    full_audio /= np.max(np.abs(full_audio))
    return full_audio

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    project_dir = "/opt/data/projects/Genres/Research/virtual_instruments"
    base_name = f"dev_metal_plate_{date_str}"
    
    fs = 44100
    t, hit, modes = create_resonant_metal_plate()
    study = generate_melodic_study(t, hit, fs)
    
    # Export paths
    wav_path = os.path.join(project_dir, f"{base_name}.wav")
    ogg_path = os.path.join(project_dir, f"{base_name}.ogg")
    
    sf.write(wav_path, study, fs)
    # Save OGG using sf (if supported) or just note it
    sf.write(ogg_path, study, fs) # soundfile supports ogg if libsndfile has it
    
    print(f"REPORT_START")
    print(f"Instrument: Resonant Metal Plate")
    print(f"Base Frequency: 120 Hz")
    print(f"Modes (Hz/Q):")
    for m in modes:
        print(f"  - f: {m['f']:.2f} Hz, Q: {m['q']}")
    print(f"Files exported to: {project_dir}")
    print(f"REPORT_END")

if __name__ == "__main__":
    main()
