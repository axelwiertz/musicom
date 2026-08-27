import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/pure_wav_test.wav"

# Kars: String synthesis
KARS_VST = "/usr/lib/vst3/Kars.vst3"

SAMPLE_RATE = 44100
DURATION = 4.0

print("--- PURE WAV TEST: Verifying Note Phrasing ---")

try:
    synth = pedalboard.load_plugin(KARS_VST)
    
    # We will use VERY long gaps and VERY distinct notes to be 100% sure.
    # 0s: C2 (36), 1s: C3 (48), 2s: C4 (60), 3s: C5 (72)
    midi_events = []
    notes = [36, 48, 60, 72]
    
    for i, note in enumerate(notes):
        # Time is total samples from 0.0
        start_tick = int(i * 1.0 * SAMPLE_RATE)
        # Note duration 0.2s
        end_tick = start_tick + int(0.2 * SAMPLE_RATE)
        
        midi_events.append(mido.Message('note_on', note=note, velocity=100, time=start_tick))
        midi_events.append(mido.Message('note_off', note=note, velocity=0, time=end_tick))

    midi_events.sort(key=lambda m: m.time)
    
    print("Rendering 4 seconds to WAV...")
    # Using the instrument-safe signature
    audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    # Normalizing to avoid any clipping/distortion
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.8 / peak)

    # Write pure WAV - no ffmpeg conversion involved yet
    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(audio)
    
    print(f"SUCCESS: WAV saved at {OUTPUT_WAV}")
    print(f"File size: {os.path.getsize(OUTPUT_WAV)} bytes")

except Exception as e:
    print(f"FAIL: {e}")
