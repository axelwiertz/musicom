import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/delta_time_test.wav"
KARS_VST = "/usr/lib/vst3/Kars.vst3"
SAMPLE_RATE = 44100
DURATION = 4.0

print("--- DELTA TIME TEST: mido message.time as relative offset ---")

try:
    synth = pedalboard.load_plugin(KARS_VST)
    
    # In Delta Time mode, 'time' is wait-time since last event.
    # 0s: Note 1 ON
    # 0.2s: Note 1 OFF
    # 0.8s wait (totals 1s): Note 2 ON
    # ...and so on.
    
    midi_events = [
        mido.Message('note_on', note=36, velocity=100, time=0),
        mido.Message('note_off', note=36, velocity=0, time=int(0.2 * SAMPLE_RATE)),
        mido.Message('note_on', note=48, velocity=100, time=int(0.8 * SAMPLE_RATE)),
        mido.Message('note_off', note=48, velocity=0, time=int(0.2 * SAMPLE_RATE)),
        mido.Message('note_on', note=60, velocity=100, time=int(0.8 * SAMPLE_RATE)),
        mido.Message('note_off', note=60, velocity=0, time=int(0.2 * SAMPLE_RATE)),
        mido.Message('note_on', note=72, velocity=100, time=int(0.8 * SAMPLE_RATE)),
        mido.Message('note_off', note=72, velocity=0, time=int(0.2 * SAMPLE_RATE))
    ]

    print("Rendering 4 seconds to WAV with DELTA TIMES...")
    audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.8 / peak)

    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(audio)
    
    print(f"SUCCESS: WAV saved at {OUTPUT_WAV}")

except Exception as e:
    print(f"FAIL: {e}")
