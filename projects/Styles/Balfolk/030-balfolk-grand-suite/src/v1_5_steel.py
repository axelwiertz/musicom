
import sys
import numpy as np
import wave
import subprocess

SAMPLE_RATE = 44100
BPM = 118
PULSE_DUR = 60.0 / (BPM * 2)

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def steel_slide_synth(freq_start, freq_end, duration, sr):
    n_samples = int(duration * sr)
    out = np.zeros(n_samples)
    
    # Dual delay lines for metallic body resonance
    delay_len = int(sr / freq_start)
    # White noise impulse
    impulse = (np.random.rand(delay_len) * 2 - 1)
    
    # Karplus-Strong buffers
    buf_main = impulse.tolist()
    buf_res  = (impulse * 0.5).tolist() # Shorter resonant body
    
    damping = 0.99
    body_res_mult = 1.58 # Inharmonic steel ratio
    
    for i in range(n_samples):
        # Glide calculation
        p = i / n_samples
        cur_f = freq_start + (freq_end - freq_start) * (p**2) # Exponential glide feel
        
        cur_delay = int(sr / cur_f)
        
        # Main string oscillation
        if len(buf_main) > cur_delay:
            buf_main = buf_main[:cur_delay]
        elif len(buf_main) < cur_delay:
            buf_main += [0] * (cur_delay - len(buf_main))
            
        val = buf_main.pop(0)
        new_val = 0.5 * (val + buf_main[0]) * damping
        buf_main.append(new_val)
        
        # Add a bit of resonance 'ping'
        out[i] = val
        
    # Envelope with sharp attack and long metallic ring
    env = np.linspace(1, 0, n_samples) ** 1.5
    return out * env

def render_v1_5_steel_suite():
    total_pulses = 144
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    # Balfolk melody with slides
    # D4 -> E4, F4 -> G4, A4 -> D5
    sequences = [
        (62, 64), (65, 67), (69, 74), (62, 62)
    ]
    
    print("Forging Steel Guitar Sound...")
    for i, (start_midi, end_midi) in enumerate(sequences):
        start_hz = midi_to_hz(start_midi)
        end_hz = midi_to_hz(end_midi)
        
        # Generate 1 bar (6 pulses) of slide
        start_idx = int(i * 6 * PULSE_DUR * SAMPLE_RATE)
        clip = steel_slide_synth(start_hz, end_hz, PULSE_DUR * 6, SAMPLE_RATE)
        
        max_len = min(len(clip), len(final_mix) - start_idx)
        final_mix[start_idx:start_idx+max_len] += clip
        
    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/steel_guitar_v1_5.ogg"
    temp_wav = "/tmp/steel_v1_5.wav"
    
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
        
    subprocess.run(f"ffmpeg -i {temp_wav} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

if __name__ == "__main__":
    print(f"DONE:{render_v1_5_steel_suite()}")
