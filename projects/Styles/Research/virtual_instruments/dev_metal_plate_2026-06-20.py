import numpy as np
import soundfile as sf
from scipy import signal
import os

# Physical Model: Resonant Metal Plate (Inharmonic Percussion)
# Using Modal Synthesis: sum of high-Q bandpass filtered noise or impulses
# Metal plates have inharmonic partial distributions

def generate_metal_plate():
    sr = 44100
    duration = 4.0  # seconds
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Base frequencies for a square metal plate (simplified)
    # Ratios for circular/square plates are roughly: 1, 1.59, 2.14, 2.3, 2.65, 2.92, 3.16, 3.5, 3.6, 4.22
    fundamental = 120.0
    ratios = [1.0, 1.59, 2.14, 2.3, 2.65, 2.92, 3.16, 3.5, 3.6, 4.22, 5.1, 7.3]
    
    # Initial "strike" - white noise burst
    strike_dur = 0.005
    strike = np.random.normal(0, 1, int(sr * strike_dur))
    strike = strike * np.hanning(len(strike))
    
    output = np.zeros_like(t)
    strike_pos = 0
    
    # Build 2-bar pattern (120 BPM, 4/4) -> 4 seconds is exactly 2 bars
    bpm = 120
    beat_dur = 60 / bpm
    pattern = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5] # Eighth notes
    
    for onset in pattern:
        start_idx = int(onset * beat_dur * sr)
        # Apply strike to the modal filters
        for i, r in enumerate(ratios):
            freq = fundamental * r
            if freq > sr / 2: continue
            
            # Modal decay - higher frequencies decay faster
            decay = 1.0 / (r * 0.8) 
            env = np.exp(-t[:int(sr * 2)] / decay)
            
            # Filtered noise or Sine with decay
            # We use a resonator approach
            # b, a = signal.iirpeak(freq, 100, sr) # High Q
            
            # Simplified modal synthesis: damped sinusoids
            mode = np.sin(2 * np.pi * freq * t[:len(env)]) * env
            
            # Randomize phase and amplitude slightly for "plate" character
            amp = 1.0 / (i + 1)
            
            end_idx = min(start_idx + len(mode), len(output))
            output[start_idx:end_idx] += mode[:end_idx-start_idx] * amp

    # Normalize
    output = output / np.max(np.abs(output))
    
    # Metrics
    metrics = {
        "fundamental": fundamental,
        "ratios": ratios,
        "decay_factor": 0.8,
        "sample_rate": sr
    }
    
    return output, sr, metrics

if __name__ == "__main__":
    audio, sr, meta = generate_metal_plate()
    
    path_prefix = "/opt/data/projects/Genres/Research/virtual_instruments/dev_metal_plate_2026-06-20"
    
    # Save WAV
    sf.write(f"{path_prefix}.wav", audio, sr)
    
    # Save OGG (Opus)
    # Using soundfile/pysoundfile if available, otherwise just use external tool if needed
    # But soundfile supports OGG via libsndfile
    try:
        sf.write(f"{path_prefix}.ogg", audio, sr, format='OGG', subtype='VORBIS')
    except:
        pass # fallback if ogg not supported by local libsndfile

    print(f"RES_PEAKS: {meta['fundamental'] * np.array(meta['ratios'])}")
    print(f"DECAY: {meta['decay_factor']}")
