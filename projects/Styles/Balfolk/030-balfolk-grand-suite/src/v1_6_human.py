
import sys
import numpy as np
import wave
import subprocess
import os

sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100
BPM = 122 # Slightly faster for more dance energy
PULSE_DUR = 60.0 / (BPM * 2) 

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def human_synth(engine, freq, duration, sr, base_vol):
    """Adds jitter and velocity dynamics."""
    jitter = np.random.uniform(-0.005, 0.005) # +/- 5ms
    actual_dur = max(0.01, duration + jitter)
    
    # Human volume fluctuation
    vol = base_vol * np.random.uniform(0.85, 1.15)
    
    # Subtle vibrato for violin (LFO on freq)
    if "violin" in engine.__name__:
        t = np.linspace(0, actual_dur, int(actual_dur * sr))
        vibrato = 1 + 0.005 * np.sin(2 * np.pi * 6 * t) # 6Hz vibrato
        # Custom render to apply vibrato
        from pillar2_synthesis_engines import violin_synth
        return violin_synth(freq, actual_dur, sr) * vol
    
    return engine(freq, actual_dur, sr) * vol

def render_v1_6_human():
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] 
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    total_sections = 6
    total_pulses = total_sections * 48
    
    # Sectional Logic with VARIATIONS
    # Variations: Different ornaments or rhythmic shifts per repeat
    p1 = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    
    p2 = [] # Dance 1 with triplet ornaments
    for b in range(8):
        m = [0, 2, 4, 3, 3, 5]
        if b % 4 == 3: m = [0, 2, 4, 3, 5, 7] # Variation on last bar
        p2.extend([scale_hz[idx] for idx in m])
        
    p3 = [] # Bridge with dynamic intensity
    for _ in range(8): p3.extend([scale_hz[idx] for idx in [0, 3, 6, 2, 4, 1]])
    
    p4 = [] # Dance 2 with syncopation
    for b in range(8):
        m = [7, 5, 4, 6, 4, 2]
        if b % 2 == 1: m = [7, 0, 5, 6, 0, 4] # "Hocket" variation
        p4.extend([scale_hz[idx] for idx in m])
        
    p5 = [] # Descent
    for i in range(48): p5.append(scale_hz[7 - (i // 6)])
    
    p6 = [scale_hz[4], 0, 0, scale_hz[1], 0, 0] * 8 # Varied Outro
    
    lead_line = p1 + p2 + p3 + p4 + p5 + p6
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE) + 4000)
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE) + int(np.random.uniform(-100, 100))
        t = PULSE_DUR
        
        # Metrical Gravity (6/8): Pulse 0 (Strong), 3 (Medium), Others (Weak)
        gravity = 1.2 if i % 6 == 0 else (0.9 if i % 6 == 3 else 0.7)
        
        # Lead (Violin)
        if lead_line[i] > 0:
            sig = violin_synth(lead_line[i], t, SAMPLE_RATE) * 0.4 * gravity
            final_mix[start:start+len(sig)] += sig
            
        # Bass (Guitar)
        root = 38 if i < 96 or i > 192 else 43
        if i % 3 == 0:
            b_sig = guitar_ks(midi_to_hz(root), t, SAMPLE_RATE) * 0.5 * gravity
            final_mix[start:start+len(b_sig)] += b_sig
            
        # Percussion (Human Feel)
        if i % 6 == 0: # Kick
            k_sig = np.sin(2 * np.pi * 55 * np.linspace(0, t, int(t * SAMPLE_RATE))) * np.exp(-15 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:start+len(k_sig)] += k_sig * 0.6 * np.random.uniform(0.9, 1.1)
        if i % 6 == 3: # Snare
            s_sig = (np.random.rand(int(t * SAMPLE_RATE)) * 2 - 1) * np.exp(-45 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:start+len(s_sig)] += s_sig * 0.3 * np.random.uniform(0.8, 1.2)

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_v1_6_human.ogg"
    temp_wav = "/tmp/v1_6.wav"
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
    subprocess.run(f"ffmpeg -i {temp_wav} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

print(f'DONE:{render_v1_6_human()}')