import pedalboard
from pedalboard.io import AudioFile
import mido
import numpy as np
import os

PROJECT_PATH = "/opt/data/projects/Styles/Electronic/031-dual-vst-study"
OUTPUT_WAV = f"{PROJECT_PATH}/audio/final_logic_test.wav"
OUTPUT_OGG = f"{PROJECT_PATH}/audio/final_logic_test.ogg"

# Kars: String synthesis
KARS_VST = "/usr/lib/vst3/Kars.vst3"

SAMPLE_RATE = 44100
DURATION = 4.0

print("--- FINAL LOGIC TEST: No-Buffer VST3 Call ---")

try:
    synth = pedalboard.load_plugin(KARS_VST)
    
    midi_events = []
    # 4 distinct notes: C3, G3, C4, G4 at 0s, 1s, 2s, 3s
    # In Pedalboard's no-buffer call, 'time' is cumulative samples from start.
    notes = [60, 67, 72, 79]
    for i, note in enumerate(notes):
        start_tick = int(i * 1.0 * SAMPLE_RATE)
        # 16th note duration (250ms)
        end_tick = start_tick + int(0.25 * SAMPLE_RATE)
        
        midi_events.append(mido.Message('note_on', note=note, velocity=100, time=start_tick))
        midi_events.append(mido.Message('note_off', note=note, velocity=0, time=end_tick))

    # SORT BY TIME - Mandatory for Pedalboard
    midi_events.sort(key=lambda m: m.time)
    
    print("Rendering with pure MIDI -> Audio signature...")
    # This signature (midi, duration, sample_rate) is the only one that works for instruments
    # without discarding the MIDI messages.
    audio = synth(midi_events, duration=DURATION, sample_rate=SAMPLE_RATE, num_channels=1)
    
    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.85 / peak)

    with AudioFile(OUTPUT_WAV, 'w', SAMPLE_RATE, 1) as f:
        f.write(audio)
    
    os.system(f"ffmpeg -y -i {OUTPUT_WAV} -codec:a libvorbis -q:a 5 {OUTPUT_OGG}")
    print(f"Final Logic Master Exported: {OUTPUT_OGG}")

except Exception as e:
    print(f"FAIL: {e}")
