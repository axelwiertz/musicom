
import sys
import numpy as np
import wave
import subprocess
import os

sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100
BPM = 118
# In 118 BPM 6/8, an eighth note (pulse) is 60 / (118 * 2)
PULSE_DUR = 60.0 / (BPM * 2) 

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def render_suite():
    from musicom_synthesis import render_wave 
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    # D Dorian scale
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] 
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    total_pulses = 192 # 32 bars * 6 pulses
    
    # 1. Lead (Violin)
    intro = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    dance = []
    for _ in range(8): dance.extend([scale_hz[idx] for idx in [0, 2, 4, 3, 3, 5]])
    bridge = []
    for _ in range(8): bridge.extend([scale_hz[idx] for idx in [0, 3, 6, 2, 4, 1]])
    # SOFTENED OUTRO: Decrescendo and return to intro motif (A4)
    outro = []
    for i in range(8):
        v_amp = 1.0 - (i/8.0)
        # Gradually transition melody back to basic A4 (scale_hz[4])
        note = scale_hz[4] if i > 4 else scale_hz[0]
        outro.extend([note, 0, 0, scale_hz[5] if i < 4 else 0, 0, 0])
    lead_line = intro + dance + bridge + outro
    
    # 2. Counterpoint (Piano)
    v2 = [0]*48 
    # Dance: Descending
    for i in range(8): v2.extend([scale_hz[7-j] for j in range(6)])
    # Bridge: Drones
    for i in range(8): v2.extend([scale_hz[0], 0, 0, scale_hz[4], 0, 0])
    # Outro: Soft chords
    for i in range(8): v2.extend([scale_hz[0] if i % 2 == 0 else 0] * 6)
    
    # 3. Bass (Guitar)
    v3 = []
    for i in range(32):
        root = scale_hz[0]/4 if (i < 16 or i > 24) else scale_hz[3]/4
        v3.extend([(root, 0.6 if j == 0 or j == 3 else 0.1) for j in range(6)])

    # 4. TYPICAL BALFOLK PERCUSSION (Tapan/Frame Drum Style)
    # Low thud on 1, slap on 4
    perc = []
    for i in range(32):
        # 1: Boom, 2: -, 3: -, 4: Tak, 5: -, 6: -
        perc.extend([('low', 0.8), ('low', 0.05), (0, 0), ('high', 0.5), (0, 0), ('high', 0.1)])

    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE))
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE)
        end = start + int(PULSE_DUR * SAMPLE_RATE)
        t = PULSE_DUR
        
        # Outro attenuation logic
        master_fader = 1.0 if i < 144 else max(0.2, 1.0 - ((i - 144) / 48.0))

        if i < len(lead_line) and lead_line[i] > 0:
            final_mix[start:end] += violin_synth(lead_line[i], t, SAMPLE_RATE) * 0.4 * master_fader
        if i < len(v2) and v2[i] > 0:
            final_mix[start:end] += piano_synth(v2[i], t, SAMPLE_RATE) * 0.2 * master_fader
        
        f_b, amp_b = v3[i]
        final_mix[start:end] += guitar_ks(f_b, t, SAMPLE_RATE) * amp_b * 0.4 * master_fader
        
        # Percussion synth (Noise + Low Sine)
        p_type, p_amp = perc[i]
        if p_type == 'low':
            # Kick-like
            kick = np.sin(2 * np.pi * 60 * np.linspace(0, t, int(t * SAMPLE_RATE))) * np.exp(-10 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += kick * p_amp * 0.5 * master_fader
        elif p_type == 'high':
            # Snare/Slap-like
            snare = (np.random.rand(int(t * SAMPLE_RATE)) * 2 - 1) * np.exp(-30 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:end] += snare * p_amp * 0.3 * master_fader

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    out_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_loop.wav"
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_loop.ogg"
    
    with wave.open(out_path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
        
    subprocess.run(f"ffmpeg -i {out_path} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

if __name__ == "__main__":
    print(f"DONE:{render_suite()}")
