
import sys
import numpy as np
import wave
import subprocess
import os

sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100
BPM = 118
PULSE_DUR = 60.0 / (BPM * 2) 

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def render_extended_suite():
    from musicom_synthesis import render_wave 
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] 
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    # 6 Sections * 8 Bars * 6 Pulses = 288 pulses
    total_sections = 6
    total_pulses = total_sections * 48
    
    # Melodic Parts
    p1 = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    p2 = []
    for _ in range(8): p2.extend([scale_hz[idx] for idx in [0, 2, 4, 3, 3, 5]])
    p3 = []
    for _ in range(8): p3.extend([scale_hz[idx] for idx in [0, 3, 6, 2, 4, 1]])
    # 4: Dance 2
    p4 = []
    for _ in range(8): p4.extend([scale_hz[idx] for idx in [7, 5, 4, 6, 4, 2]])
    # 5: Descent
    p5 = []
    for i in range(48): p5.append(scale_hz[7 - (i // 6)])
    p6 = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
        
    lead_line = p1 + p2 + p3 + p4 + p5 + p6
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE)
        end = start + int(PULSE_DUR * SAMPLE_RATE)
        t = PULSE_DUR
        sec = i // 48
        master_fader = 1.0 if sec < 4 else max(0.3, 1.0 - ((i - 192) / 96.0))

        if i < len(lead_line) and lead_line[i] > 0:
            final_mix[start:end] += violin_synth(lead_line[i], t, SAMPLE_RATE) * 0.4 * master_fader
            
        if i % 6 == 0:
            kick = np.sin(2 * np.pi * 60 * np.linspace(0, t, int(t * SAMPLE_RATE))) * np.exp(-12 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += kick * 0.4 * master_fader
        if i % 6 == 3:
            snare = (np.random.rand(int(t * SAMPLE_RATE)) * 2 - 1) * np.exp(-40 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += snare * 0.2 * master_fader

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    out_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_extended.wav"
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_extended.ogg"
    
    with wave.open(out_path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
    
    subprocess.run(f"ffmpeg -i {out_path} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

print(f'DONE:{render_extended_suite()}')