import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

# Project Config
PROJECT_PATH = "/opt/data/projects/Styles/Electronic/030-acid-matrix-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/acid_loop.wav"
OUTPUT_OGG = f"{PROJECT_PATH}/audio/acid_loop.ogg"
VST3_PATH = "/usr/lib/vst3/Nekobi.vst3"

SAMPLE_RATE = 44100
BPM = 128
STEP_DUR = 60 / (BPM * 4)  # 16th note duration
TOTAL_STEPS = 16
DURATION = STEP_DUR * TOTAL_STEPS

# Acid Pattern (D-Minor)
# (Note, Velocity, Gate_Length_Factor)
# .75 = 16th note, 0 = rest, .95 = held for slide feel
pattern = [
    (38, 110, 0.75), (0, 0, 0),        (38, 90, 0.75),  (50, 120, 0.95),  # Slide up to D3
    (38, 100, 0.75), (41, 100, 0.75),  (38, 90, 0.75),  (0, 0, 0),
    (36, 115, 0.95), (38, 100, 0.75),  (0, 0, 0),       (41, 110, 0.75),
    (43, 100, 0.75), (41, 95, 0.75),   (38, 110, 0.75), (38, 80, 0.4)
]

print(f"--- Project 030: {VST3_PATH} HQ Render ---")

try:
    # 1. Load Plugin
    synth = pedalboard.load_plugin(VST3_PATH)
    print(f"Loaded {synth.name}")
    
    # 2. Build MIDI Events
    midi_events = []
    current_time = 0.0
    for note, vel, gate in pattern:
        if note > 0:
            start_tick = int(current_time * SAMPLE_RATE)
            end_tick = int((current_time + (STEP_DUR * gate)) * SAMPLE_RATE)
            midi_events.append(mido.Message('note_on', note=note, velocity=vel, time=start_tick))
            midi_events.append(mido.Message('note_off', note=note, velocity=0, time=end_tick))
        current_time += STEP_DUR

    # 3. Render
    print(f"Rendering {DURATION:.2f}s loop...")
    audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    # 4. Save
    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(audio)
    
    # 5. Convert to OGG (Opus)
    os.system(f"ffmpeg -y -i {OUTPUT_WAV} -codec:a libvorbis -q:a 5 {OUTPUT_OGG}")
    print(f"Delivery Ready: {OUTPUT_OGG}")

except Exception as e:
    print(f"ERROR: {e}")
