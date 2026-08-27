
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

def render_v1_3_suite():
    from musicom_synthesis import render_wave 
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] 
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    total_sections = 6
    total_pulses = total_sections * 48
    
    # Lead (Violin)
    p1 = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    p2 = []
    for _ in range(8): p2.extend([scale_hz[idx] for idx in [0, 2, 4, 3, 3, 5]])
    p3 = []
    for _ in range(8): p3.extend([scale_hz[idx] for idx in [0, 3, 6, 2, 4, 1]])
    
    # Part 4 NEW HARMONY: Smoothing out the turnaround, removing C# (73)
    p4 = []
    for _ in range(8): p4.extend([scale_hz[idx] for idx in [7, 5, 4, 6, 4, 2]]) # D, C, A, B, A, F
    
    p5 = []
    for i in range(48): p5.append(scale_hz[7 - (i // 6)])
    p6 = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    v1_line = p1 + p2 + p3 + p4 + p5 + p6
    
    # Rest of voices
    v2_p1 = [0] * 48
    v2_p2 = []
    for i in range(8): v2_p2.extend([scale_hz[7-j] for j in range(6)])
    v2_p3 = []
    for i in range(8): v2_p3.extend([scale_hz[0], 0, 0, scale_hz[4], 0, 0])
    v2_p4 = [] # Synchronized Piano
    for i in range(8): v2_p4.extend([scale_hz[0], scale_hz[2], scale_hz[4], scale_hz[0], scale_hz[3], scale_hz[5]])
    v2_p5 = [scale_hz[0]] * 48
    v2_p6 = [0] * 48
    v2_line = v2_p1 + v2_p2 + v2_p3 + v2_p4 + v2_p5 + v2_p6

    v3_line = []
    for i in range(total_sections):
        root = 38 if i != 2 else 43
        for j in range(48):
            amp = 0.6 if j % 3 == 0 else 0.1
            v3_line.append((midi_to_hz(root), amp))

    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE)
        end = start + int(PULSE_DUR * SAMPLE_RATE)
        t = PULSE_DUR
        sec = i // 48
        v_main = 1.0 if sec < 4 else max(0.2, 1.0 - ((i - 192) / 96.0))

        if v1_line[i] > 0:
            final_mix[start:end] += violin_synth(v1_line[i], t, SAMPLE_RATE) * 0.4 * v_main
        if v2_line[i] > 0:
            final_mix[start:end] += piano_synth(v2_line[i], t, SAMPLE_RATE) * 0.2 * v_main
        f_b, a_b = v3_line[i]
        final_mix[start:end] += guitar_ks(f_b, t, SAMPLE_RATE) * a_b * 0.4 * v_main
        if i % 6 == 0:
            kick = np.sin(2 * np.pi * 60 * np.linspace(0, t, int(t * SAMPLE_RATE))) * np.exp(-12 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += kick * 0.5 * v_main
        if i % 6 == 3:
            snare = (np.random.rand(int(t * SAMPLE_RATE)) * 2 - 1) * np.exp(-40 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += snare * 0.3 * v_main

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_v1_3.ogg"
    temp_wav = "/tmp/v1_3.wav"
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
    subprocess.run(f"ffmpeg -i {temp_wav} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

print(f'DONE:{render_v1_3_suite()}')