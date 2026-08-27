import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/concatenated_test.wav"
KARS_VST = "/usr/lib/vst3/Kars.vst3"
SAMPLE_RATE = 44100
NOTE_DURATION = 1.0  # 1 second segments

print("--- CONCATENATED BUFFER TEST: Rendering notes individually ---")

try:
    synth = pedalboard.load_plugin(KARS_VST)
    print(f"Loaded: {synth.name}")
    
    notes = [60, 67, 72, 79]
    all_buffers = []

    for note in notes:
        # Create a single Note On at sample 0 for this specific segment
        # In this mode, we provide ONLY the events for THIS duration
        event_on = mido.Message('note_on', note=note, velocity=100, time=0)
        event_off = mido.Message('note_off', note=note, velocity=0, time=int(0.5 * SAMPLE_RATE))
        
        # Render exactly 1 second of audio for this note
        # reset=True ensures the synth re-triggers/resets its internal state
        print(f"  Rendering Note {note}...")
        buffer = synth([event_on, event_off], duration=NOTE_DURATION, sample_rate=SAMPLE_RATE, num_channels=1, reset=True)
        all_buffers.append(buffer)

    # Combine the four 1-second buffers
    final_audio = np.concatenate(all_buffers, axis=1)
    
    # Normalize
    peak = np.max(np.abs(final_audio))
    if peak > 0:
        final_audio = final_audio * (0.85 / peak)

    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(final_audio)
    
    print(f"SUCCESS: Concatenated WAV saved at {OUTPUT_WAV}")

except Exception as e:
    print(f"FAIL: {e}")
