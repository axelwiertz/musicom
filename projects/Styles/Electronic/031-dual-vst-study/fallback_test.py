import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/fallback_vst_test.wav"
OUTPUT_OGG = f"{PROJECT_PATH}/audio/fallback_vst_test.ogg"

# Kars: A Karplus-Strong string synthesis plugin from DPF collection
KARS_VST = "/usr/lib/vst3/Kars.vst3"

SAMPLE_RATE = 44100
DURATION = 4.0

print("--- FALLBACK TEST: Kars (String Synth) ---")

try:
    synth = pedalboard.load_plugin(KARS_VST)
    print(f"Loaded: {synth.name}")
    
    midi_events = []
    # 4 distinct notes: C3, G3, C4, G4
    notes = [60, 67, 72, 79]
    for i, note in enumerate(notes):
        start_time = i * 0.75 # 750ms spacing - very obvious gaps
        end_time = start_time + 0.4
        
        # Cumulative sample offsets for Pedalboard
        midi_events.append(mido.Message('note_on', note=note, velocity=100, time=int(start_time * SAMPLE_RATE)))
        midi_events.append(mido.Message('note_off', note=note, velocity=0, time=int(end_time * SAMPLE_RATE)))

    midi_events.sort(key=lambda m: m.time)
    
    print("Rendering String pluck sequence...")
    # NOTE: Kars might be mono or stereo; let's try 1 channel first
    audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    # Normalize to -1dB
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.89 / peak)

    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(audio)
    
    os.system(f"ffmpeg -y -i {OUTPUT_WAV} -codec:a libvorbis -q:a 5 {OUTPUT_OGG}")
    print(f"Fallback Master Exported: {OUTPUT_OGG}")

except Exception as e:
    print(f"FAIL: {e}")
