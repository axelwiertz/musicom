
import sys
import numpy as np
import wave
import subprocess

SAMPLE_RATE = 44100
BPM = 118
PULSE_DUR = 60.0 / (BPM * 2)

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def steel_guitar_synth(freq, duration, sr, slide_to=None):
    """Karplus-Strong with damping and optional frequency slide."""
    n_samples = int(duration * sr)
    out = np.zeros(n_samples)
    
    # Initialize delay buffer with noise (the pluck)
    delay = int(sr / freq)
    ring_buffer = (np.random.rand(delay) * 2 - 1).tolist()
    
    # Damping factor: high for metallic string
    damping = 0.99 
    
    for i in range(n_samples):
        # Frequency slide implementation (Linear interpolation of delay length)
        if slide_to:
            current_freq = freq + (slide_to - freq) * (i / n_samples)
            current_delay = int(sr / max(current_freq, 10))
            if current_delay != delay:
                # Rescale buffer (simple crop/pad for slide effect)
                if current_delay < delay:
                    ring_buffer = ring_buffer[:current_delay]
                else:
                    ring_buffer += [0] * (current_delay - delay)
                delay = current_delay
        
        # Pull from buffer
        val = ring_buffer.pop(0)
        # Low-pass filter (average) + Damping
        new_val = damping * 0.5 * (val + ring_buffer[0])
        ring_buffer.append(new_val)
        out[i] = val
        
    # Apply envelope
    env = np.exp(-4 * np.linspace(0, 1, n_samples))
    return out * env

def render_v1_4_steel():
    total_pulses = 288 # 6 sections
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    # Target frequencies for slide (Steel Guitar Part)
    # Slide from D4 to E4 (62 to 64)
    start_hz = midi_to_hz(62)
    end_hz = midi_to_hz(64)
    
    print("Synthesizing Steel Guitar Glides...")
    for i in range(total_pulses):
        start_idx = int(i * PULSE_DUR * SAMPLE_RATE)
        # Every 24 pulses, add a slide
        if i % 24 == 0:
            slide = steel_guitar_synth(start_hz, PULSE_DUR * 12, SAMPLE_RATE, slide_to=end_hz)
            length = min(len(slide), len(final_mix) - start_idx)
            final_mix[start_idx:start_idx+length] += slide * 0.7

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/test_steel_v1_4.ogg"
    temp_wav = "/tmp/steel.wav"
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
    subprocess.run(f"ffmpeg -i {temp_wav} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

if __name__ == "__main__":
    print(f"DONE:{render_v1_4_steel()}")
