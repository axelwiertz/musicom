
import sys
import numpy as np
import wave
import subprocess
import os

# Consolidated Library
sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100
BPM = 118
PULSE_DUR = 60.0 / (BPM * 2) # Eighth note

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def generate_polyphonic_suite():
    from musicom_synthesis import render_wave 
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] # D Dorian
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    # 32 bars total (192 pulses)
    total_pulses = 192
    
    # 1. Voice: Lead (Violin) - The Melody
    intro = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    dance_indices = [0, 2, 4, 3, 3, 5]
    dance = []
    for _ in range(8): dance.extend([scale_hz[idx] for idx in dance_indices])
    bridge_indices = [0, 3, 6, 2, 4, 1] 
    bridge = []
    for _ in range(8): bridge.extend([scale_hz[idx] for idx in bridge_indices])
    climax = [scale_hz[i % len(scale_hz)] for i in range(48)]
    lead_line = intro + dance + bridge + climax
    
    # 2. Voice: Counterpoint (Piano fallback for Pluck) - Modal support
    # Descending counter-melody to the dance
    counter_line = [0] * 48 # Intro quiet
    for i in range(48): # Dance section counter
        idx = (7 - (i // 6)) % 8
        counter_line.append(scale_hz[idx])
    for i in range(48): # Bridge drones
        counter_line.append(scale_hz[0] if i % 12 < 6 else scale_hz[4])
    for i in range(48): # Outro chaos
        counter_line.append(scale_hz[(i*2) % 8])

    # 3. Voice: Bass (Guitar KS) - Rhythmic Foundation
    bass_line = []
    for i in range(total_pulses):
        is_strong = (i % 3 == 0)
        p_bass = midi_to_hz(38) if (i % 6 < 3) else midi_to_hz(43)
        bass_line.append((p_bass, 0.7 if is_strong else 0.1))

    # Synthesis Loop
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    print(f"Rendering 3-Voice Polyphonic Suite...")
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE)
        end = start + int(PULSE_DUR * SAMPLE_RATE)
        
        # Lead
        if lead_line[i] > 0:
            final_mix[start:end] += violin_synth(lead_line[i], PULSE_DUR, SAMPLE_RATE) * 0.5
            
        # Counterpoint
        if counter_line[i] > 0:
            final_mix[start:end] += piano_synth(counter_line[i], PULSE_DUR, SAMPLE_RATE) * 0.3
            
        # Bass
        f_b, amp_b = bass_line[i]
        final_mix[start:end] += guitar_ks(f_b, PULSE_DUR, SAMPLE_RATE) * amp_b * 0.4
        
    # Final production
    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    
    out_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_poly.wav"
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_poly.ogg"
    
    with wave.open(out_path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        audio_int16 = (np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
        
    subprocess.run(f"ffmpeg -i {out_path} -codec:a libopus -application voip -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

if __name__ == "__main__":
    try:
        res = generate_polyphonic_suite()
        print(f"DONE:{res}")
    except Exception as e:
        print(f"ERROR:{e}")
